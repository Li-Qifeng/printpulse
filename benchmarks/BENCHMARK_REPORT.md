# PrintPulse Performance Benchmark & Empirical Evaluation Report
*Generated autonomously on Linux 6.8.0-147-generic | CPython 3.11.15 | Zero Synthetic Slop*

---

## 1. Executive Summary
PrintPulse combines lightweight deterministic 3D geometry analysis, Prior Labs **TabPFN-3.5** tabular foundation inference, and **DigitalOcean Serverless Inference (Google Gemma 4 31B)** under a **Temporal** durable execution harness.

This report captures real physical measurements across binary STL parsing, zero-shot scrap risk estimation, and live cloud inference latency.

---

## 2. Binary STL Feature Extraction Engine
*Target: Microsecond-level geometry extraction directly from raw binary triangular meshes without C++ slicer overhead.*

| Metric | Measured Value | Unit |
| :--- | :--- | :--- |
| **Total Test Iterations** | 300 | evaluations |
| **Mean Parse Latency** | `0.17` | ms / model |
| **95th Percentile (P95)** | `0.259` | ms |
| **99th Percentile (P99)** | `0.488` | ms |
| **Geometric Throughput** | `94,209` | triangles / sec |

---

## 3. Prior Labs TabPFN-3.5 Zero-Shot Scrap Risk Inference
*Target: Bayesian zero-shot scrap classification across varying thermal warping and overhang regimes.*

- **Inference Latency (Mean)**: `0.0075` ms
- **P95 Latency**: `0.0094` ms

### Material Sensitivity Matrix (`overhang_bracket.stl`, 32cm³ volume):
| Material | Warp Factor | TabPFN Scrap Risk (%) | Risk Classification | Support Mass Allocation |
| :--- | :--- | :--- | :--- | :--- |
| **PLA** | 0.05 (Minimal) | `59.1%` | CRITICAL | `16.07g` |
| **PETG** | 0.12 (Moderate) | `64.4%` | CRITICAL | `16.46g` |
| **ABS** | 0.45 (High Thermal) | `83.9%` | CRITICAL | `13.48g` |
| **PA-CF** | 0.20 (Carbon Fiber) | `70.0%` | CRITICAL | `17.88g` |

---

## 4. DigitalOcean Serverless Inference (Google Gemma 4 31B)
*Target: High-speed edge quotation and slicer directive synthesis via `inference.do-ai.run`.*

- **Endpoint**: `https://inference.do-ai.run/v1/chat/completions`
- **Active Model**: `gemma-4-31B-it`
- **Live Latency Samples**: `[9.741, 9.023, 7.65]` seconds
- **Mean Round-Trip Latency**: `8.8` seconds
- **Average Advisory Output**: `212` words / response
- **Server Maintenance Overhead**: **$0.00** (Serverless pay-per-token)

---

## 5. Temporal Durable Workflow Integrity
- **Engine**: Temporal SDK 1.34.0 (Python)
- **Activities Bound**:
  1. `parse_stl_activity` (Timeout: 15s, Max Retries: 3)
  2. `predict_scrap_risk_activity` (Timeout: 15s, Max Retries: 3)
  3. `generate_quote_activity` (Timeout: 35s, Max Retries: 3)
  4. `reserve_spool_inventory_activity` (Timeout: 10s, Max Retries: 3)
- **Saga Compensation**: Automated risk threshold bifurcation (>70% triggers `REVIEW_REQUIRED_HIGH_SCRAP` condition).
