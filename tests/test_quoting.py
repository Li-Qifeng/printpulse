from dataclasses import asdict
from src.stl_analyzer import parse_stl
from src.tabpfn_predictor import TabPFNScrapPredictor
from src.do_quoting_agent import DigitalOceanQuotingAgent

def test_financial_breakdown_math():
    cube = parse_stl("/root/printpulse/models/calibration_cube.stl")
    predictor = TabPFNScrapPredictor()
    pred = predictor.predict_risk(asdict(cube), material="PETG")

    agent = DigitalOceanQuotingAgent()
    quote = agent.generate_quote(asdict(cube), asdict(pred), material="PETG")

    # Math verification: total = material + machine + risk_buffer
    expected_subtotal = round(quote.material_cost_usd + quote.machine_cost_usd + quote.scrap_risk_buffer_usd, 2)
    assert abs(quote.subtotal_production_usd - expected_subtotal) <= 0.02
    
    expected_final = round(quote.subtotal_production_usd + quote.profit_margin_usd, 2)
    assert abs(quote.final_quote_usd - expected_final) <= 0.02
    assert quote.final_quote_usd > 0.0

def test_risk_buffer_scaling():
    cube = parse_stl("/root/printpulse/models/calibration_cube.stl")
    bracket = parse_stl("/root/printpulse/models/overhang_bracket.stl")
    predictor = TabPFNScrapPredictor()

    pred_cube = predictor.predict_risk(asdict(cube), material="PETG")
    pred_bracket = predictor.predict_risk(asdict(bracket), material="PETG")

    agent = DigitalOceanQuotingAgent()
    quote_cube = agent.generate_quote(asdict(cube), asdict(pred_cube), material="PETG")
    quote_bracket = agent.generate_quote(asdict(bracket), asdict(pred_bracket), material="PETG")

    # Bracket with high overhang scrap risk must allocate significantly higher scrap risk buffer
    assert quote_bracket.scrap_risk_buffer_usd > quote_cube.scrap_risk_buffer_usd
