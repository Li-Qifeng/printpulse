"""
Synthetic STL Generator for Test Fixtures
Generates valid binary STL files for unit testing and benchmarking:
1. calibration_cube.stl (20x20x20mm, flat faces, 0% overhang)
2. overhang_bracket.stl (L-bracket with severe 90-degree overhangs)
3. tall_tower.stl (10x10x120mm, high aspect ratio, bed adhesion risk)
"""

import math
import struct
import os

def write_binary_stl(filepath: str, triangles: list[tuple[tuple[float, float, float], list[tuple[float, float, float]]]]):
    header = b"PrintPulse Synthetic Test Fixture" + b"\x00" * (80 - len(b"PrintPulse Synthetic Test Fixture"))
    num_triangles = len(triangles)
    
    with open(filepath, "wb") as f:
        f.write(header)
        f.write(struct.pack("<I", num_triangles))
        for normal, vertices in triangles:
            # Normal vector (3 floats)
            f.write(struct.pack("<3f", *normal))
            # 3 Vertices (3 floats each)
            for v in vertices:
                f.write(struct.pack("<3f", *v))
            # Attribute byte count (uint16)
            f.write(struct.pack("<H", 0))

def compute_normal(v1, v2, v3):
    ax, ay, az = v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]
    bx, by, bz = v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]
    nx = ay * bz - az * by
    ny = az * bx - ax * bz
    nz = ax * by - ay * bx
    norm = math.sqrt(nx * nx + ny * ny + nz * nz)
    if norm > 1e-9:
        return (nx / norm, ny / norm, nz / norm)
    return (0.0, 0.0, 1.0)

def generate_box(width: float, depth: float, height: float, z_offset: float = 0.0) -> list:
    x0, x1 = 0.0, width
    y0, y1 = 0.0, depth
    z0, z1 = z_offset, z_offset + height

    p = [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), # bottom 0..3
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)  # top 4..7
    ]

    quads = [
        # Bottom (z0) - normal (0, 0, -1)
        (p[0], p[2], p[1]), (p[0], p[3], p[2]),
        # Top (z1) - normal (0, 0, 1)
        (p[4], p[5], p[6]), (p[4], p[6], p[7]),
        # Front (y0) - normal (0, -1, 0)
        (p[0], p[1], p[5]), (p[0], p[5], p[4]),
        # Back (y1) - normal (0, 1, 0)
        (p[2], p[3], p[7]), (p[2], p[7], p[6]),
        # Left (x0) - normal (-1, 0, 0)
        (p[0], p[4], p[7]), (p[0], p[7], p[3]),
        # Right (x1) - normal (1, 0, 0)
        (p[1], p[2], p[6]), (p[1], p[6], p[5]),
    ]

    triangles = []
    for v1, v2, v3 in quads:
        normal = compute_normal(v1, v2, v3)
        triangles.append((normal, [v1, v2, v3]))
    return triangles

def create_test_fixtures(output_dir: str = "/root/printpulse/models"):
    os.makedirs(output_dir, exist_ok=True)

    # 1. Calibration Cube (20x20x20mm)
    cube_tris = generate_box(20.0, 20.0, 20.0)
    write_binary_stl(os.path.join(output_dir, "calibration_cube.stl"), cube_tris)

    # 2. Tall Tower (10x10x120mm - Aspect ratio 12.0, severe tipping risk)
    tower_tris = generate_box(10.0, 10.0, 120.0)
    write_binary_stl(os.path.join(output_dir, "tall_tower.stl"), tower_tris)

    # 3. Overhang Bracket (T-Shaped Cantilever: Base 20x20x10, Top Overhang 80x20x10 floating at Z=40)
    # The overhang creates 60mm of unsupported downward-facing horizontal area (normal = 0, 0, -1)
    base = generate_box(20.0, 20.0, 40.0)
    cantilever = generate_box(80.0, 20.0, 10.0, z_offset=40.0)
    bracket_tris = base + cantilever
    write_binary_stl(os.path.join(output_dir, "overhang_bracket.stl"), bracket_tris)

    print(f"Generated 3 test fixtures in {output_dir}:")
    print(f"  - calibration_cube.stl ({len(cube_tris)} triangles)")
    print(f"  - tall_tower.stl ({len(tower_tris)} triangles)")
    print(f"  - overhang_bracket.stl ({len(bracket_tris)} triangles)")

if __name__ == "__main__":
    create_test_fixtures()
