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

## Data Files

### Energy Balance Excel Files (exported from LEAP)
| File | Scenario | Format |
|---|---|---|
| `Book7.xlsx`, `Book8.xlsx`, `Book9.xlsx` | BAU | Multi-sheet (one sheet per year, tab named `...\|YYYY`) |
| `LMI Energy Balance.xlsx` | LMI | Single-sheet (years as columns, Unmet Requirements in row 17) |
| `Updated Pro Solar.xlsx` | Pro-Solar | Single-sheet (same format as LMI) |
| `Updated UT.xlsx` | Utility Protection | Single-sheet (same format as LMI) |

### Other Data Files
| File | Description |
|---|---|
| `Full Scenario Excel LEAP.xlsx` | Complete LEAP scenario export with all settings (5331 rows × 55 cols) |
| `LEAP Scenario Updated BAU.xlsx` | BAU scenario parameters |
| `S3_scenario_assumptions.xlsx` | Scenario assumption inputs |

## Key Scripts

All in `s3-scenario/`:

| Script | Purpose |
|---|---|
| `scenario_comparison_figure.py` | **Main output script** — generates SSEG capacity figure, supply-demand balance figure, and CSV comparison for all 4 scenarios |
| `bass_diffusion_bau.py` | BAU Bass diffusion adoption model |
| `bass_diffusion_s3.py` | Multi-scenario Bass diffusion model |
| `revenue_erosion_s3.py` | Revenue impact analysis |
| `generate_excel.py` | Generate Excel exports |
| `unmet_requirements_analysis.py` | Unmet requirements deep-dive |

### Running the Main Script
```bash
pip install openpyxl matplotlib
python s3-scenario/scenario_comparison_figure.py
```
Outputs: `scenario_sseg_capacity.png`, `scenario_supply_demand_balance.png`, `unmet_requirements_comparison.csv`

## Known Issue: Fixed Imports in Pro-solar/UP

BAU and LMI show dynamic (decreasing) centralized imports as SSEG grows, but Pro-solar and Utility Protection have imports **fixed at 5874 GWh**. Root cause: Dispatch Rule=4 dispatches by historical share, and Cape Town IPP Solar/Wind have Historical Production=0, so they never dispatch despite growing capacity. Additionally, DG Surplus Rule=2 sends surplus to the Solar feedstock resource, not the grid — so only the demand-side Grid/SHS household split affects centralized generation requirements.

**Fix**: In LEAP GUI, change Cape Town IPP Solar/Wind to a capacity-based dispatch rule, or seed their Historical Production with a non-zero value. Then recalculate all scenarios.

## Color Theme
- BAU: Gray `#666666`
- LMI Subsidy: Teal `#2A9D8F`
- Pro-Solar: Gold `#E9C46A`
- Utility Protection: Coral `#E76F51`

## Working Language
The user communicates primarily in Chinese (Mandarin). Technical terms and code remain in English.
