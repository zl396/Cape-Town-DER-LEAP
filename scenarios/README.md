# Scenarios — Analytical work for the 4 LEAP scenarios

This directory holds all scripts, data outputs, and methodology docs for the
four-scenario study (BAU / LMI Subsidy / Pro-Solar / Utility Protection).

## Layout

| Subdir | Purpose | Read this when… |
|---|---|---|
| `comparison/` | **Main deliverable** — 4-scenario cross-comparison figures + script | You want the canonical SSEG capacity / supply-demand balance / energy balance figures |
| `bass-diffusion/` | Bass-diffusion adoption model (per-scenario adoption curves) | You want to inspect or rerun the SSEG adoption modeling that produces the capacity inputs |
| `revenue/` | Utility revenue-erosion analysis | You want avoided-generation and revenue-impact numbers |
| `unmet/` | Standalone unmet-requirements analysis | You want a deeper view of just the unmet/load-shedding side |
| `diagnostics/` | Debugging tools used during the May 1 Eskom-IPP-capacity bug investigation | You suspect a future scenario has stuck-imports or similar — these scripts will surface settings differences fast |
| `docs/` | LEAP implementation guides + methodology docs | You're onboarding to the LEAP model itself |
| `inputs/` | Scenario assumption inputs (`S3_scenario_assumptions.xlsx`) | You want the source assumptions feeding the Bass model |
| `tools/` | Utility scripts | One-off helpers like `generate_excel.py` |

## Where the canonical figures live

```
comparison/scenario_sseg_capacity_v3.png         ← SSEG capacity by scenario
comparison/scenario_supply_demand_balance_v3.png ← Publication-style supply-demand gap
comparison/scenario_energy_balance_v3.png        ← 3-panel diagnostic (Production/Imports/Unmet)
comparison/scenario_comparison_v3.csv            ← Long-format data dump for downstream
comparison/scenario_comparison_v3.py             ← Build script (regenerates all 3 figs + CSV)
```

`comparison/archive/` holds the v1 figures from before the May 1 Eskom IPP capacity fix — kept so that prior commits remain reproducible against the data they referenced.

## Where the input data lives

Energy Balance Excel exports (canonical) are at the **repo-root** path:
```
data/current/        ← 4 v3 Energy Balance exports (read these)
data/leap-export/    ← Full Scenario Excel + other model snapshots
data/archive/        ← Stale Energy Balance exports preserved for traceability
```

## How to regenerate the canonical figures

```bash
cd <repo-root>
python scenarios/comparison/scenario_comparison_v3.py
```

Outputs are written next to the script (`scenarios/comparison/`).
