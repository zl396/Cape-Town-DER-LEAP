# Cape Town DER-LEAP: Session Work Log

## Project Overview

Cape Town Distributed Energy Resources (DER) study using LEAP (Long-range Energy Alternatives Planning) to model 4 policy scenarios for rooftop solar (SSEG) adoption and their impact on the city's electricity supply-demand balance (2018-2050).

### Four Scenarios

| Scenario | Policy | Bass Diffusion | 2050 SSEG (MW) |
|---|---|---|---|
| BAU | Current trajectory | Standard p, q, m | 845 |
| LMI Subsidy | Government subsidies for low/mid income | Higher p for Low/Mid | 1,182 |
| Pro-Solar | Feed-in tariffs, streamlined permits | Higher m (saturation cap) | 1,207 |
| Utility Protection | Restrictive tariffs, grid fees | Dampened p ≈ 0 | 359 |

### Key Parameters
- **Bass Diffusion Model**: p (innovation), q (imitation), m (saturation cap)
- **3 Income Groups**: High (HomeUser tariff, 4.91 kW mean), Mid (Domestic, 3.66 kW), Low (LifeLine, 2.84 kW)
- **Commercial Multiplier**: Total SSEG = Residential x 1.25
- **LEAP Transformation**: Dispatch Rule=4, Surplus Rule=2 (DG), Shortfall Rule=1 (Electricity Gen)

---

## Work Completed This Session

### 1. Data Alignment on "Updated BAU" Area

**Problem**: The original Pro-solar and Utility Protection scenarios were built on different LEAP Areas, causing 2018-2023 historical data misalignment.

**Fix**: All 4 scenarios rebuilt on the "Updated BAU" Area. Verified that 2018-2023 Energy Balance values are now identical across all scenarios:
- 2018 Unmet: -0.87 GWh
- 2019 Unmet: -3.17 GWh
- 2020 Unmet: -5.66 GWh
- 2021 Unmet: -6.55 GWh
- 2022 Unmet: -7.44 GWh
- 2023 Unmet: 0.00 GWh

### 2. Updated SSEG Capacity Data

Replaced outdated Pro-solar and Utility Protection SSEG Interp values in `scenario_comparison_figure.py` with corrected values from LEAP Data View.

**Pro-solar** (corrected, all 33 years):
```
{2018:9.549, 2019:18.073, 2020:33.162, 2021:59.787, 2022:108.707,
 2023:165.050, 2024:230.948, 2025:350.945, 2026:480.678, 2027:611.136,
 2028:732.659, 2029:799.597, 2030:843.153, ... 2050:1206.923}
```

**Utility Protection** (corrected, all 33 years):
```
{2018:9.55, 2019:18.06, 2020:33.02, 2021:59.83, 2022:108.64,
 2023:164.95, 2024:183.689, 2025:200.576, 2026:215.733, 2027:229.219,
 2028:241.075, 2029:251.406, 2030:260.383, ... 2050:359.216}
```

### 3. Updated Energy Balance Sources

Changed `load_all_unmet()` in `scenario_comparison_figure.py`:
- Pro-solar: `'Updated Pro Solar.xlsx'` (was hardcoded override)
- Utility Protection: `'Updated UT.xlsx'` (was `'Utility Protection Energy Balance.xlsx'`)
- Removed `PROSOLAR_UNMET_OVERRIDE` hardcoded dict entirely

### 4. Figure Color Theme Update

Changed from old colors to match reference image:
| Scenario | Old Color | New Color | Hex |
|---|---|---|---|
| BAU | Gray #888888 | Gray | #666666 |
| LMI | Blue #2166AC | Teal | #2A9D8F |
| Pro-solar | Green #1B7837 | Gold | #E9C46A |
| Utility Protection | Red #B2182B | Coral | #E76F51 |

### 5. Generated Outputs

- `scenario_sseg_capacity.png` — Projected SSEG Installed Capacity by Scenario (2018-2050)
- `scenario_supply_demand_balance.png` — Projected Supply-Demand Balance by Scenario (2018-2050)
- `unmet_requirements_comparison.csv` — All 4 scenarios, yearly SSEG (MW) and Unmet (GWh)

### Summary Table (from script output)
```
Scenario                2030 SSEG  2050 SSEG 2024-33 Deficit 2034-50 Surplus
                             (MW)       (MW)           (GWh)           (GWh)
---------------------------------------------------------------------------
BAU                           590        845            3168           -6958
LMI                           780       1182            1789          -14732
Pro-solar                     843       1207            2057          -17841
Utility Protection            260        359            6478            -130
```

---

## Known Issue: Fixed Imports in Pro-solar and Utility Protection

### Symptom
BAU and LMI show dynamic (decreasing) centralized imports over time, while Pro-solar and Utility Protection have imports fixed at 5874 GWh throughout the projection period.

### Analysis (from Full Scenario Excel LEAP.xlsx)

Examined all 5331 rows x 55 columns. Found:
- **Only 1 Transformation difference** across scenarios: SSEG Exogenous Capacity (expected)
- **41 Demand differences**: Grid Only vs Grid+SHS household Activity Level splits (expected)
- **Everything else identical**: Dispatch Rule, Merit Order, Capacity, Surplus Rule, etc.

### Root Cause Hypothesis

1. **Dispatch Rule = 4 ("Percent of Requirement")**: Each generation process dispatches based on its **historical share** of total requirement.

2. **Cape Town IPP Solar and Wind have Historical Production = 0**: Under DR=4, these processes have 0% historical share and therefore **never dispatch**, even as their capacity grows (Solar: 0→200 MW, Wind: 0→600 MW by 2035+).

3. **DG Surplus Rule = 2 = "Add Exports to Feedstock"**: SSEG surplus goes back to Solar resource, NOT directly to the grid. So SSEG does not reduce the requirement seen by the Electricity Generation module. Only the demand-side Grid/SHS split matters.

4. **Shortfall Rule = 1 = "Add Imports"**: The gap between centralized output and requirement becomes imports.

### Recommended Fix (in LEAP GUI)
- Change Cape Town IPP Solar/Wind Dispatch Rule from 4 to 1 or 2 (Merit Order or Capacity-based)
- OR set a non-zero Historical Production seed value for these processes
- Recalculate all 4 scenarios after changes

---

## File Structure

```
Cape-Town-DER-LEAP/
├── Book7.xlsx, Book8.xlsx, Book9.xlsx    # BAU Energy Balance (year-by-year sheets)
├── LMI Energy Balance.xlsx               # LMI Energy Balance
├── Updated Pro Solar.xlsx                # Pro-solar Energy Balance (corrected)
├── Updated UT.xlsx                       # Utility Protection Energy Balance (corrected)
├── Full Scenario Excel LEAP.xlsx         # Complete LEAP scenario export (all settings)
├── s3-scenario/
│   ├── scenario_comparison_figure.py     # Main script: generates both figures + CSV
│   ├── scenario_sseg_capacity.png        # Figure 1: SSEG capacity by scenario
│   ├── scenario_supply_demand_balance.png # Figure 2: Supply-demand balance
│   ├── unmet_requirements_comparison.csv # Data export for all scenarios
│   ├── bass_diffusion_bau.py             # BAU Bass diffusion model
│   ├── bass_diffusion_s3.py              # S3 (multi-scenario) Bass diffusion
│   ├── WORK_LOG.md                       # This file
│   └── ...
```

---

## Commit History (this branch: claude/leap-new-scenarios-nGs1y)

```
5599ecf Regenerate figures and CSV with all corrected scenario data
ec5b3ca Add files via upload
a79aaea Update supply-demand balance figure with corrected Energy Balance data
4390a28 Update figure color theme to match reference (gray/teal/gold/coral)
13ec98a Update SSEG capacity data with corrected Pro-solar and Utility Protection values
d605d34 Add files via upload
```
