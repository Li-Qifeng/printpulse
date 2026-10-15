from dataclasses import asdict
from src.tabpfn_predictor import TabPFNScrapPredictor
from src.stl_analyzer import parse_stl

def test_reference_dataset_loaded():
    predictor = TabPFNScrapPredictor()
    assert predictor.X_train.shape[0] >= 50
    assert predictor.X_train.shape[1] == 5
    assert len(predictor.y_train) == predictor.X_train.shape[0]

def test_cube_low_risk():
    cube = parse_stl("/root/printpulse/models/calibration_cube.stl")
    predictor = TabPFNScrapPredictor()
    pred = predictor.predict_risk(asdict(cube), material="PLA")
    
    assert pred.predicted_failure_probability < 0.35
    assert pred.recommended_support_mass_g == 0.0
    assert pred.recommended_brim_raft is False

def test_tower_high_slenderness_tipping():
    tower = parse_stl("/root/printpulse/models/tall_tower.stl")
    predictor = TabPFNScrapPredictor()
    pred = predictor.predict_risk(asdict(tower), material="PETG")
    
    assert pred.risk_tier == "CRITICAL"
    assert pred.predicted_failure_probability > 0.80
    assert pred.recommended_brim_raft is True
    assert "Bed Detachment" in pred.primary_failure_mode

def test_bracket_support_estimation():
    bracket = parse_stl("/root/printpulse/models/overhang_bracket.stl")
    predictor = TabPFNScrapPredictor()
    pred = predictor.predict_risk(asdict(bracket), material="PETG")
    
    assert pred.recommended_support_mass_g > 10.0
    assert pred.confidence_interval_low < pred.predicted_failure_probability < pred.confidence_interval_high

def test_material_warping_sensitivity():
    bracket = parse_stl("/root/printpulse/models/overhang_bracket.stl")
    predictor = TabPFNScrapPredictor()
    pla_pred = predictor.predict_risk(asdict(bracket), material="PLA")
    abs_pred = predictor.predict_risk(asdict(bracket), material="ABS")
    
    # ABS has significantly higher thermal warping shrinkage and failure rate than PLA on complex overhangs
    assert abs_pred.predicted_failure_probability > pla_pred.predicted_failure_probability
