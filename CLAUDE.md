# Cape Town DER-LEAP Project

## What This Project Is

A Cape Town Distributed Energy Resources (DER) study using LEAP (Long-range Energy Alternatives Planning) to model **4 policy scenarios** for rooftop solar (SSEG) adoption and their impact on the city's electricity supply-demand balance (2018-2050). The goal is to evaluate whether DER adoption can mitigate load shedding under different policy environments.

## The 4 Scenarios

| Scenario | Policy Description | Bass Diffusion Change | 2050 SSEG (MW) |
|---|---|---|---|
| **BAU** | Current trajectory, no policy change | Standard p, q, m | 845 |
| **LMI Subsidy** | Government subsidies targeting low/mid income households | Higher p (innovation) for Low/Mid income | 1,182 |
| **Pro-Solar** | Feed-in tariffs, streamlined permits, net metering | Higher m (saturation cap) for all groups | 1,207 |
| **Utility Protection** | Restrictive tariffs, grid access fees, bureaucratic barriers | Dampened p ≈ 0, adoption only via peer effects | 359 |

## Key Technical Details

### SSEG Adoption Model
- **Bass Diffusion Model** with parameters: p (innovation coefficient), q (imitation coefficient), m (saturation cap)
- **3 Income Groups**: High (HomeUser tariff, mean 4.91 kW), Mid (Domestic, 3.66 kW), Low (LifeLine, 2.84 kW)
- **Commercial Multiplier**: Total SSEG = Residential × 1.25
- Capacity values are input to LEAP as **Interp expressions** (year-value pairs)

### LEAP Model Settings
- All scenarios built on **"Updated BAU" Area** (ensures aligned 2018-2023 historical baseline)
- **Dispatch Rule = 4** ("Percent of Requirement") for centralized Electricity Generation
- **Surplus Rule = 2** ("Add Exports to Feedstock") for Distributed Generation
- **Shortfall Rule = 1** ("Add Imports") for Electricity Generation
- T&D losses: 10.59%

### Energy Balance Equation
```
Production (SSEG) + Imports (centralized grid) = Demand + T&D Losses + Unmet Requirements
```
- Positive Unmet = deficit (load shedding)
- Negative Unmet = surplus generation

## Repo Structure

```
data/
  current/        ← 4 v3 EB files (May 1) — analysis reads from here
  leap-export/    ← Full Scenario Excel + other model snapshots
  archive/        ← Stale EB exports (kept for traceability)
model/            ← .leap file + scenario assumption inputs
references/       ← PDFs and DOCX (papers, dissertations, reports)
analysis/         ← Earlier analysis outputs (DER load shedding study)
ai-agent-engineering/  ← AI methodology docs
scenarios/        ← All scenario analytical work, organized by purpose:
  README.md         (layout map)
  WORK_LOG.md       (session history)
  comparison/       (canonical 4-scenario figures + script)
    archive/        (v1 figures from before May 1 fix)
  bass-diffusion/   (per-scenario adoption modeling)
  revenue/          (utility revenue-erosion analysis)
  unmet/            (unmet-requirements deep-dive)
  diagnostics/      (debug tools from May 1 investigation)
  docs/             (LEAP implementation guides + methodology)
  inputs/           (S3_scenario_assumptions.xlsx)
  tools/            (generate_excel.py)
```

## Canonical Data Files

### Current Energy Balance exports (use these — `data/current/`)
| File | Scenario | Notes |
|---|---|---|
| `BAU EB v3.xlsx` | Updated BAU GHS | Multi-sheet — explicitly read sheet `'Energy Balance'` (sheet 0 has UP contamination) |
| `LMI EB v3.xlsx` | Updated LMI GHS | Single sheet |
| `Pro Solar EB v3.xlsx` | Updated Pro Solar | Single sheet |
| `UP EB v3.xlsx` | Updated Utility Protection | Single sheet |

All v3 files exported May 1 after Eskom IPP capacity was restored (see Known Issue below). Format: rows = Production / Imports / Exports / Total Primary Supply / Electricity Generation / T&D / DG / Transformation / Households / LPUs / SPUs / Municipality / Total Demand / **Unmet Requirements** (row 17). Cols 2-34 = years 2018-2050.

### LEAP model snapshots (`data/leap-export/`)
| File | Description |
|---|---|
| `Full Scenario Excel LEAP.xlsx` | Complete LEAP scenario export with all settings (5331 rows × 55 cols, all 9 scenarios × all variables) |
| `LEAP Scenario Updated BAU.xlsx` | BAU scenario parameters |

### Stale exports (`data/archive/`)
- `Book5-9.xlsx`, `LMI Energy Balance.xlsx`, `Pro-solar Energy Balance.xlsx`, `Updated Pro Solar.xlsx`, `Updated UT.xlsx`, etc. — superseded by v3. Kept so prior commits remain reproducible.

## Key Scripts

| Script | Path | Purpose |
|---|---|---|
| **`scenario_comparison_v3.py`** | `scenarios/comparison/` | **Main canonical output** — generates SSEG capacity figure, supply-demand balance figure, energy balance 3-panel, and CSV (reads from `data/current/`) |
| `bass_diffusion_bau.py` | `scenarios/bass-diffusion/` | BAU Bass diffusion adoption model |
| `bass_diffusion_s3.py` | `scenarios/bass-diffusion/` | Multi-scenario Bass diffusion model |
| `revenue_erosion_s3.py` | `scenarios/revenue/` | Revenue impact analysis |
| `unmet_requirements_analysis.py` | `scenarios/unmet/` | Unmet requirements deep-dive (note: paths still reference pre-reorg data locations — fix if rerunning) |
| `generate_excel.py` | `scenarios/tools/` | Generate Excel exports |
| `imports_diagnostic_comparison.py` | `scenarios/diagnostics/` | May 1 debug tool: cross-scenario Imports trend (note: stale paths) |
| `ipp_settings_diff.py` | `scenarios/diagnostics/` | May 1 debug tool: scan IPP settings across all 9 scenarios (note: stale paths) |

`scenarios/comparison/archive/scenario_comparison_figure.py` is the v1 script kept for historical reference. Don't run it — it reads from `data/archive/` paths that no longer match repo root.

### Running the Main Script
```bash
pip install openpyxl matplotlib
python scenarios/comparison/scenario_comparison_v3.py
```
Outputs (in `scenarios/comparison/`): `scenario_sseg_capacity_v3.png`, `scenario_supply_demand_balance_v3.png`, `scenario_energy_balance_v3.png`, `scenario_comparison_v3.csv`

## Resolved Issue: "Imports stuck at 5874 GWh" (May 1, fixed)

**Symptom (Apr 13 → May 1 19:22)**: Pro-solar and UP Energy Balance exports showed Imports plateau at exactly 5874 GWh from 2024 onward, while older BAU/LMI Apr 3 exports showed dynamic decline.

**False hypotheses (ruled out)**:
- Stale exports — re-running Calculate produced the same 5874 cap
- Dispatch Rule = 4 with Historical Production = 0 — verified IPP settings were identical across all 4 Updated scenarios

**True root cause** (found by comparing all 9 scenarios in `Full Scenario Excel LEAP.xlsx`): The 4 Updated scenarios (uBAU, uLMI, uPS, uUP) had **Eskom IPP Exogenous Capacity slashed** vs the original BAU/LMIHI scenarios:

| Process | Updated 2050 (broken) | BAU 2050 (correct) |
|---|---|---|
| Eskom Wind | **3 MW** | 1,474 MW |
| Eskom IPP Solar | 93 MW | 778 MW |
| Eskom IPP OCGT | 32 MW | 166 MW |

The Apr 3 BAU/LMI exports came from BEFORE this reduction → looked normal. Apr 13 Pro-solar/UP came AFTER → 5874 GWh was the residual gap that imports had to fill.

**Fix applied** (May 1 19:34): User restored Eskom IPP Exogenous Capacity in LEAP. All 4 Updated scenarios re-exported (`data/current/*.xlsx`). 2050 Imports now ranges 1,210-1,260 GWh across scenarios (dynamic decline from 8,867).

## Outstanding Issue: UP "exact 0 Unmet" from 2036+

Utility Protection scenario shows Unmet Requirements = exactly 0 from 2036 to 2050. Suspected LEAP constraint (Maximum Imports cap or Minimum Production floor) enforcing balance rather than physical equilibrium. Sanity-check before citing.

## Color Theme
- BAU: Gray `#666666`
- LMI Subsidy: Teal `#2A9D8F`
- Pro-Solar: Gold `#E9C46A`
- Utility Protection: Coral `#E76F51`

## Working Language
The user communicates primarily in Chinese (Mandarin). Technical terms and code remain in English.
