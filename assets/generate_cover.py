"""
Generates 1000x420 DEV.to Hacktoberfest Cover Image for PrintPulse
"""

import asyncio
from playwright.async_api import async_playwright

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1000px;
    height: 420px;
    background: radial-gradient(circle at 75% 30%, #1e1b4b 0%, #090d16 65%, #030712 100%);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #f8fafc;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 48px 56px;
  }
  .grid-bg {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: 
      linear-gradient(to right, rgba(59, 130, 246, 0.08) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(59, 130, 246, 0.08) 1px, transparent 1px);
    background-size: 32px 32px;
    pointer-events: none;
  }
  .header-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    background: rgba(30, 58, 138, 0.5);
    border: 1px solid rgba(96, 165, 250, 0.4);
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 600;
    color: #93c5fd;
    letter-spacing: 0.05em;
    width: fit-content;
  }
  .main-title {
    font-size: 42px;
    font-weight: 800;
    line-height: 1.15;
    background: linear-gradient(135deg, #ffffff 0%, #93c5fd 60%, #60a5fa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-top: 14px;
    max-width: 680px;
  }
  .subtitle {
    font-size: 18px;
    color: #94a3b8;
    margin-top: 12px;
    max-width: 620px;
    line-height: 1.4;
  }
  .tech-pills {
    display: flex;
    gap: 12px;
    align-items: center;
  }
  .pill {
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 700;
    background: #111827;
    border: 1px solid #1f2937;
    color: #cbd5e1;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .pill-do { border-color: #0284c7; color: #38bdf8; background: rgba(2, 132, 199, 0.12); }
  .pill-tab { border-color: #8b5cf6; color: #c084fc; background: rgba(139, 92, 246, 0.12); }
  .pill-temp { border-color: #10b981; color: #34d399; background: rgba(16, 185, 129, 0.12); }

  .stat-card {
    position: absolute;
    right: 56px;
    bottom: 52px;
    width: 250px;
    background: rgba(17, 24, 39, 0.85);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
  }
  .stat-label { font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 700; }
  .stat-val { font-size: 26px; font-weight: 800; color: #38bdf8; margin: 4px 0; }
  .stat-desc { font-size: 12px; color: #94a3b8; }
</style>
</head>
<body>
  <div class="grid-bg"></div>

  <div>
    <div class="header-badge">
      <span>● HACKTOBERFEST 2026 WEEK 2</span>
      <span style="color: #60a5fa;">// SIDE HUSTLE</span>
    </div>
    <h1 class="main-title">PrintPulse</h1>
    <p class="subtitle">Autonomous 3D Print Farm Scrap Risk Predictor & Quoting Agent</p>
  </div>

  <div class="stat-card">
    <div class="stat-label">TabPFN Bayesian Zero-Shot</div>
    <div class="stat-val">0.0075 ms</div>
    <div class="stat-desc">Microsecond scrap prediction & auto-calibrated risk buffers</div>
  </div>

  <div class="tech-pills">
    <div class="pill pill-do">DigitalOcean Serverless (Gemma 4 31B)</div>
    <div class="pill pill-tab">Prior Labs TabPFN-3.5</div>
    <div class="pill pill-temp">Temporal Durable Workflows</div>
  </div>
</body>
</html>
"""

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1000, "height": 420})
        await page.set_content(HTML)
        await page.screenshot(path="/root/printpulse/assets/cover.png")
        await browser.close()
        print("Generated /root/printpulse/assets/cover.png")

if __name__ == "__main__":
    asyncio.run(run())
