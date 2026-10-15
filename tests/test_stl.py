import os
import pytest
from src.stl_analyzer import parse_stl, STLGeometryMetrics

FIXTURES_DIR = "/root/printpulse/models"

def test_calibration_cube_geometry():
    path = os.path.join(FIXTURES_DIR, "calibration_cube.stl")
    metrics = parse_stl(path)
    assert metrics.dim_x_mm == pytest.approx(20.0, abs=0.1)
    assert metrics.dim_y_mm == pytest.approx(20.0, abs=0.1)
    assert metrics.dim_z_mm == pytest.approx(20.0, abs=0.1)
    assert metrics.volume_cm3 == pytest.approx(8.0, abs=0.1)
    assert metrics.surface_area_cm2 == pytest.approx(24.0, abs=0.1)
    assert metrics.overhang_area_cm2 == 0.0
    assert metrics.overhang_ratio == 0.0
    assert metrics.aspect_ratio == 1.0

def test_tall_tower_slenderness():
    path = os.path.join(FIXTURES_DIR, "tall_tower.stl")
    metrics = parse_stl(path)
    assert metrics.dim_z_mm == pytest.approx(120.0, abs=0.1)
    assert metrics.aspect_ratio == pytest.approx(12.0, abs=0.1)
    assert metrics.slenderness_index > 8.0

def test_overhang_bracket_detection():
    path = os.path.join(FIXTURES_DIR, "overhang_bracket.stl")
    metrics = parse_stl(path)
    assert metrics.overhang_area_cm2 > 10.0
    assert metrics.overhang_ratio > 0.15
    assert metrics.projected_support_cm3 > 20.0

def test_invalid_stl_handling():
    with pytest.raises(FileNotFoundError):
        parse_stl("/root/printpulse/models/non_existent.stl")
