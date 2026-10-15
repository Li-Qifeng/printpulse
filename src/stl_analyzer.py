"""
PrintPulse Fast Binary/ASCII STL Geometric Feature Extractor
Extracts exact physical parameters directly from STL meshes without heavy C++ slicer dependencies:
- Bounding Box Dimensions (X, Y, Z in mm)
- Volume (cm3 via signed tetrahedron divergence theorem)
- Surface Area (cm2)
- Overhang Surface Area & Overhang Ratio (faces tilted > 45 degrees relative to Z-up)
- Aspect Ratio & Slenderness (Z / min(X, Y) tipping vulnerability)
- Base Contact Area (Z = 0 adhesion surface)
- Projected Support Volume Estimate (heuristic voxel column drop)
"""

import math
import struct
import os
from dataclasses import dataclass, asdict

@dataclass
class STLGeometryMetrics:
    filename: str
    file_size_kb: float
    num_triangles: int
    dim_x_mm: float
    dim_y_mm: float
    dim_z_mm: float
    volume_cm3: float
    surface_area_cm2: float
    base_contact_area_cm2: float
    overhang_area_cm2: float
    overhang_ratio: float           # Overhang area / Total surface area
    aspect_ratio: float             # Height / min(width, depth)
    slenderness_index: float        # Height / sqrt(Base contact area)
    projected_support_cm3: float    # Estimated support volume needed

def parse_stl(filepath: str) -> STLGeometryMetrics:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"STL file not found: {filepath}")
    
    file_size = os.path.getsize(filepath)
    if file_size < 84:
        raise ValueError("Invalid STL file: size < 84 bytes")

    with open(filepath, "rb") as f:
        header = f.read(80)
        num_triangles_bytes = f.read(4)
        num_triangles = struct.unpack("<I", num_triangles_bytes)[0]

        # Sanity check if it is binary: 80 + 4 + 50 * N == file_size
        expected_size = 84 + num_triangles * 50
        is_binary = (expected_size == file_size)

        if not is_binary:
            raise NotImplementedError("ASCII STL parser not implemented in minimal pass; standard binary STL required.")

        min_x = min_y = min_z = float("inf")
        max_x = max_y = max_z = float("-inf")
        
        total_volume_mm3 = 0.0
        total_surface_area_mm2 = 0.0
        overhang_area_mm2 = 0.0
        base_contact_area_mm2 = 0.0
        
        # We will collect downward faces with their centroid Z and area to estimate support volume
        overhang_faces = []

        for _ in range(num_triangles):
            record = f.read(50)
            if len(record) < 50:
                break
            
            # Normal (3f), V1 (3f), V2 (3f), V3 (3f), Attr (1H)
            data = struct.unpack("<12fH", record)
            nx, ny, nz = data[0], data[1], data[2]
            v1 = (data[3], data[4], data[5])
            v2 = (data[6], data[7], data[8])
            v3 = (data[9], data[10], data[11])

            # Update bounding box
            for v in (v1, v2, v3):
                min_x = min(min_x, v[0])
                max_x = max(max_x, v[0])
                min_y = min(min_y, v[1])
                max_y = max(max_y, v[1])
                min_z = min(min_z, v[2])
                max_z = max(max_z, v[2])

            # Cross product for area and exact normal calculation
            ax, ay, az = v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]
            bx, by, bz = v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]
            cx = ay * bz - az * by
            cy = az * bx - ax * bz
            cz = ax * by - ay * bx
            cross_mag = math.sqrt(cx * cx + cy * cy + cz * cz)
            face_area = 0.5 * cross_mag
            total_surface_area_mm2 += face_area

            # Exact normal unit vector
            if cross_mag > 1e-9:
                unx, uny, unz = cx / cross_mag, cy / cross_mag, cz / cross_mag
            else:
                unx, uny, unz = 0.0, 0.0, 1.0

            # Signed volume of tetrahedron with origin
            # V = (1/6) * |v1 . (v2 x v3)|
            vol = (v1[0] * (v2[1] * v3[2] - v2[2] * v3[1]) +
                   v1[1] * (v2[2] * v3[0] - v2[0] * v3[2]) +
                   v1[2] * (v2[0] * v3[1] - v2[1] * v3[0])) / 6.0
            total_volume_mm3 += vol

            # Overhang detection:
            # In standard 3D printing:
            # - unz = 1.0 is pointing straight up (0 deg from vertical)
            # - unz = 0.0 is vertical wall (90 deg from vertical)
            # - unz < -0.7071 is pointing downward > 45 degrees! Needs support!
            # - unz == -1.0 is flat ceiling facing the print bed
            if unz < -0.7071:
                # Check if it touches the bottom bed (Z min)
                avg_z = (v1[2] + v2[2] + v3[2]) / 3.0
                if abs(avg_z - min_z) < 0.5 and unz < -0.99:
                    base_contact_area_mm2 += face_area
                else:
                    overhang_area_mm2 += face_area
                    overhang_faces.append((face_area, avg_z))

    dim_x = max(0.0, max_x - min_x)
    dim_y = max(0.0, max_y - min_y)
    dim_z = max(0.0, max_z - min_z)
    
    volume_cm3 = abs(total_volume_mm3) / 1000.0
    surface_area_cm2 = total_surface_area_mm2 / 100.0
    overhang_area_cm2 = overhang_area_mm2 / 100.0
    base_contact_area_cm2 = base_contact_area_mm2 / 100.0

    overhang_ratio = (overhang_area_cm2 / surface_area_cm2) if surface_area_cm2 > 0 else 0.0
    min_horizontal_span = min(dim_x, dim_y) if min(dim_x, dim_y) > 0 else 1.0
    aspect_ratio = dim_z / min_horizontal_span

    base_eff_radius = math.sqrt(base_contact_area_cm2 * 100.0 / math.pi) if base_contact_area_cm2 > 0 else 0.1
    slenderness_index = dim_z / (base_eff_radius * 2.0)

    # Estimate support volume: sum(overhang_area * height_above_bed)
    support_vol_mm3 = 0.0
    for area, z in overhang_faces:
        height_drop = max(0.0, z - min_z)
        support_vol_mm3 += area * height_drop * 0.45  # 45% support infill density
    projected_support_cm3 = support_vol_mm3 / 1000.0

    return STLGeometryMetrics(
        filename=os.path.basename(filepath),
        file_size_kb=round(file_size / 1024.0, 2),
        num_triangles=num_triangles,
        dim_x_mm=round(dim_x, 2),
        dim_y_mm=round(dim_y, 2),
        dim_z_mm=round(dim_z, 2),
        volume_cm3=round(volume_cm3, 3),
        surface_area_cm2=round(surface_area_cm2, 2),
        base_contact_area_cm2=round(base_contact_area_cm2, 2),
        overhang_area_cm2=round(overhang_area_cm2, 2),
        overhang_ratio=round(overhang_ratio, 4),
        aspect_ratio=round(aspect_ratio, 2),
        slenderness_index=round(slenderness_index, 2),
        projected_support_cm3=round(projected_support_cm3, 3)
    )

if __name__ == "__main__":
    import json
    for name in ["calibration_cube.stl", "tall_tower.stl", "overhang_bracket.stl"]:
        path = f"/root/printpulse/models/{name}"
        if os.path.exists(path):
            m = parse_stl(path)
            print(f"--- {name} ---")
            print(json.dumps(asdict(m), indent=2))
