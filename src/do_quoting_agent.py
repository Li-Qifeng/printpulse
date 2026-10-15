"""
PrintPulse Quoting Agent powered by DigitalOcean Serverless Inference
Leverages Google Gemma 4 (gemma-4-31B-it) hosted on DigitalOcean Serverless Inference:
Endpoint: https://inference.do-ai.run/v1/chat/completions

Synthesizes physical geometric metrics, TabPFN risk probabilities, and machine economics
into a professional, client-facing manufacturing quote and production advisory.
"""

import os
import json
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict

# Material costs per kg (USD)
MATERIAL_COST_PER_KG = {
    "PLA": 18.00,
    "PETG": 22.00,
    "ABS": 20.00,
    "ASA": 26.00,
    "TPU": 32.00,
    "PC": 45.00,
    "PA-CF": 65.00
}

# Machine operational cost per hour (Depreciation, electricity, nozzle wear)
DEFAULT_MACHINE_HOURLY_RATE = 3.50
DEFAULT_TARGET_MARGIN = 0.40  # 40% gross margin

@dataclass
class ProductionQuote:
    filename: str
    material: str
    total_print_time_hours: float
    net_filament_grams: float
    support_filament_grams: float
    total_filament_grams: float
    material_cost_usd: float
    machine_cost_usd: float
    scrap_risk_buffer_usd: float
    subtotal_production_usd: float
    profit_margin_usd: float
    final_quote_usd: float
    llm_advisory_report: str
    provider: str
    model: str

class DigitalOceanQuotingAgent:
    def __init__(self, do_token: str | None = None, model: str = "gemma-4-31B-it"):
        self.do_token = do_token or os.environ.get("DIGITALOCEAN_TOKEN", "")
        self.endpoint = "https://inference.do-ai.run/v1/chat/completions"
        self.model = model

    def estimate_print_time_hours(self, metrics: dict, support_mass_g: float) -> float:
        """
        Calculates realistic print duration on modern high-speed CoreXY 3D printers (e.g. Bambu P1/X1, Voron 2.4).
        Volume flow rate ~ 15 mm3/s, with travel, layer change, and retractions.
        """
        volume_mm3 = metrics.get("volume_cm3", 10.0) * 1000.0
        # Support volume is printed at roughly 20 mm3/s
        support_mm3 = (support_mass_g / 1.25) * 1000.0
        
        # Extrusion time in seconds
        extrusion_seconds = (volume_mm3 * 0.35) / 12.0 + (support_mm3) / 18.0
        
        # Layer change overhead
        dim_z_mm = metrics.get("dim_z_mm", 20.0)
        layer_count = dim_z_mm / 0.20  # 0.20mm standard layer height
        layer_overhead_seconds = layer_count * 1.8
        
        # Bed heating, mesh leveling, nozzle purge wipe (12 minutes fixed)
        startup_seconds = 12 * 60
        
        total_seconds = startup_seconds + extrusion_seconds + layer_overhead_seconds
        hours = max(0.35, round(total_seconds / 3600.0, 2))
        return hours

    def generate_quote(self,
                       stl_metrics: dict,
                       tabpfn_prediction: dict,
                       material: str = "PETG",
                       machine_hourly_rate: float = DEFAULT_MACHINE_HOURLY_RATE,
                       target_margin: float = DEFAULT_TARGET_MARGIN) -> ProductionQuote:
        mat = material.upper()
        kg_price = MATERIAL_COST_PER_KG.get(mat, 22.00)
        
        total_grams = tabpfn_prediction.get("total_estimated_mass_g", 15.0)
        support_grams = tabpfn_prediction.get("recommended_support_mass_g", 0.0)
        net_grams = max(0.0, total_grams - support_grams)
        failure_prob = tabpfn_prediction.get("predicted_failure_probability", 0.05)
        
        print_hours = self.estimate_print_time_hours(stl_metrics, support_grams)
        
        # Financial Calculations
        material_cost = (total_grams / 1000.0) * kg_price
        machine_cost = print_hours * machine_hourly_rate
        base_cost = material_cost + machine_cost
        
        # Scrap Risk Buffer: Prior Labs TabPFN Bayesian failure rate pricing
        # If risk is 10%, we price in 10% expected loss; if 60%, we buffer heavily to cover reprint cost
        risk_buffer = base_cost * failure_prob * 1.25
        
        total_production = base_cost + risk_buffer
        profit = total_production * target_margin
        final_price = total_production + profit

        # Prompt DigitalOcean Gemma-4-31B-it for engineering advisory & customer brief
        advisory_text = self._call_digitalocean_llm(stl_metrics, tabpfn_prediction, mat, final_price, print_hours)

        return ProductionQuote(
            filename=stl_metrics.get("filename", "unknown.stl"),
            material=mat,
            total_print_time_hours=round(print_hours, 2),
            net_filament_grams=round(net_grams, 2),
            support_filament_grams=round(support_grams, 2),
            total_filament_grams=round(total_grams, 2),
            material_cost_usd=round(material_cost, 2),
            machine_cost_usd=round(machine_cost, 2),
            scrap_risk_buffer_usd=round(risk_buffer, 2),
            subtotal_production_usd=round(total_production, 2),
            profit_margin_usd=round(profit, 2),
            final_quote_usd=round(final_price, 2),
            llm_advisory_report=advisory_text,
            provider="DigitalOcean Serverless Inference",
            model=self.model
        )

    def _call_digitalocean_llm(self, metrics: dict, prediction: dict, material: str, quote_usd: float, print_hours: float) -> str:
        overhang_ratio_pct = (metrics.get('overhang_ratio') or 0.0) * 100.0
        failure_prob_pct = (prediction.get('predicted_failure_probability') or 0.0) * 100.0

        prompt = f"""
You are PrintPulse, an autonomous engineering quoting agent for high-precision 3D print farms.
Evaluate this manufacturing request and generate a concise engineering advisory report.

[Physical Metrics]
- File: {metrics.get('filename')}
- Dimensions: {metrics.get('dim_x_mm')}mm x {metrics.get('dim_y_mm')}mm x {metrics.get('dim_z_mm')}mm
- Net Volume: {metrics.get('volume_cm3')} cm3
- Overhang Surface Area: {metrics.get('overhang_area_cm2')} cm2 ({overhang_ratio_pct:.1f}%)
- Slenderness Tipping Index: {metrics.get('slenderness_index')}
- Material: {material}
- Estimated Print Duration: {print_hours} hours
- Quoted Price: ${quote_usd:.2f}

[TabPFN Zero-Shot Scrap Prediction]
- Failure Risk Probability: {failure_prob_pct:.1f}% ({prediction.get('risk_tier')})
- Primary Failure Mode: {prediction.get('primary_failure_mode')}
- Support Material Needed: {prediction.get('recommended_support_mass_g')}g
- Brim / Adhesion Raft Recommended: {prediction.get('recommended_brim_raft')}

Provide:
1. Executive Manufacturing Decision (Accept / Conditional Review / Reject)
2. Slicer Optimization Directives (Infill type, support interface density, cooling speed)
3. Client Transparency Summary (Why the price is fair, how scrap risk is safeguarded)
Keep it sharp, technical, and professional.
"""
        req_body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are PrintPulse, an elite 3D print farm operational intelligence agent."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 500
        }
        
        headers = {
            "Authorization": f"Bearer {self.do_token}",
            "Content-Type": "application/json"
        }

        try:
            req = urllib.request.Request(self.endpoint, data=json.dumps(req_body).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            # Deterministic fallback report if offline
            return f"[Offline Fallback Advisory]: File {metrics.get('filename')} evaluated. Risk tier: {prediction.get('risk_tier')}. TabPFN indicated failure mode: {prediction.get('primary_failure_mode')}. Recommended brim: {prediction.get('recommended_brim_raft')}. Quoted price: ${quote_usd:.2f}."

if __name__ == "__main__":
    from stl_analyzer import parse_stl
    from tabpfn_predictor import TabPFNScrapPredictor

    analyzer = parse_stl("/root/printpulse/models/overhang_bracket.stl")
    predictor = TabPFNScrapPredictor()
    pred = predictor.predict_risk(asdict(analyzer), material="PETG")

    agent = DigitalOceanQuotingAgent()
    quote = agent.generate_quote(asdict(analyzer), asdict(pred), material="PETG")
    print(json.dumps(asdict(quote), indent=2))
