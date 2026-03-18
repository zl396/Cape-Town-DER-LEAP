# LEAP Implementation Guide: S3 Progressive Subsidy Scenario

## Overview

Step-by-step instructions for entering the **S3 Progressive Subsidy** scenario into the LEAP model. This scenario **inherits from the Updated BAU** — only values that differ need to be entered.

See `LEAP_BAU_implementation_guide.md` for the BAU setup (must be completed first).

**S3 Policy Design:**
- Higher saturation targets than BAU (30/25/15% vs 25/15/3%)
- Progressive subsidy: Low-income gets largest policy boost (2.5x), Mid-income moderate (1.5x), High-income no subsidy (market-driven)
- Commercial multiplier: 1.25x on SSEG capacity

**Data Source (v3 — corrected 2026-03-16):**
- Same corrected income groups and household counts as BAU
- Bass diffusion calibrated on 2022-2023 Mask2Former data, then policy multipliers applied to p
- 2018-2023 values identical to BAU (policy divergence starts 2024)

---

## Step 1: Create the S3 Scenario

1. **Analysis → Manage Scenarios** → Add
2. **Name:** `S3 Progressive Subsidy`
3. **Inherit from:** `Business-As-Usual (BAU)`
4. Only values that differ from BAU need to be entered below

---

## Step 2: Demand Side — High-Income (m=30%, no subsidy)

Navigate to: **High Income → Grid and SHS** (in S3 scenario)

Bass parameters: p=0.036070, q=0.38
```
Interp(2018, 0.50, 2019, 0.88, 2020, 1.56, 2021, 2.74, 2022, 4.84, 2023, 7.29, 2024, 10.21, 2025, 13.48, 2026, 16.90, 2027, 20.17, 2028, 23.04, 2029, 25.32, 2030, 26.99, 2035, 29.76, 2040, 29.98, 2045, 30.00, 2050, 30.00)
```

Grid Only: `Remainder(100)`

---

## Step 3: Demand Side — Mid-Income (m=25%, p=1.5x)

Bass parameters: p=0.054105, q=0.30
```
Interp(2018, 0.10, 2019, 0.22, 2020, 0.47, 2021, 1.01, 2022, 2.18, 2023, 3.28, 2024, 5.31, 2025, 7.63, 2026, 10.16, 2027, 12.77, 2028, 15.31, 2029, 17.61, 2030, 19.57, 2035, 24.20, 2040, 24.91, 2045, 24.99, 2050, 25.00)
```

Grid Only: `Remainder(100)`

---

## Step 4: Demand Side — Low-Income (m=15%, p=2.5x)

Bass parameters: p=0.090175, q=0.19
```
Interp(2018, 0.00, 2019, 0.13, 2020, 0.26, 2021, 0.38, 2022, 0.51, 2023, 0.64, 2024, 2.05, 2025, 3.56, 2026, 5.10, 2027, 6.64, 2028, 8.09, 2029, 9.42, 2030, 10.59, 2035, 13.92, 2040, 14.78, 2045, 14.96, 2050, 14.99)
```

Grid Only: `Remainder(100)`

---

## Step 5: Supply Side — S3 SSEG Capacity

Total SSEG = residential capacity x 1.25 (commercial estimate):
```
Interp(2018, 10, 2019, 18, 2020, 33, 2021, 60, 2022, 110, 2023, 165, 2024, 246, 2025, 339, 2026, 439, 2027, 539, 2028, 632, 2029, 713, 2030, 780, 2035, 954, 2040, 1036, 2045, 1107, 2050, 1182)
```

Capacity factor: **19.6%** (SOEC 2021)

---

## BAU vs S3 Comparison

| Year | BAU HI | S3 HI | BAU MI | S3 MI | BAU LI | S3 LI |
|---|---|---|---|---|---|---|
| 2023 | 7.29% | 7.29% | 3.28% | 3.28% | 0.64% | 0.64% |
| 2025 | 13.10% | 13.48% | 5.93% | 7.63% | 0.94% | 3.56% |
| 2030 | 23.35% | 26.99% | 12.35% | 19.57% | 1.79% | 10.59% |
| 2040 | 24.99% | 29.98% | 14.95% | 24.91% | 2.81% | 14.78% |
| 2050 | 25.00% | 30.00% | 15.00% | 25.00% | 2.98% | 14.99% |

| Year | BAU SSEG (MW) | S3 SSEG (MW) | Difference |
|---|---|---|---|
| 2025 | 303 | 339 | +36 MW |
| 2030 | 590 | 780 | +190 MW |
| 2035 | 687 | 954 | +267 MW |
| 2040 | 741 | 1,036 | +295 MW |
| 2050 | 845 | 1,182 | +337 MW |

---

## Verification

After entering S3 values, press **F5** to run. Check:

1. **Activity levels**: "Grid Only" + "Grid and SHS" = 100% for each group
2. **S3 > BAU**: All adoption curves should be above or equal to BAU
3. **2018-2023 identical**: BAU and S3 should overlap before 2024 (policy divergence)
4. **S3 2050 SSEG generation**: ~2,028 GWh (1,182 MW x 19.6% x 8,760h)
5. **Load shedding**: S3 should show reduced unmet requirements vs BAU

---

## Bass Model Parameters (S3)

| Group | p | q | m (saturation) | Policy multiplier |
|---|---|---|---|---|
| High | 0.036070 | 0.38 | 30% | 1.0x (no subsidy) |
| Mid | 0.054105 | 0.30 | 25% | 1.5x on p |
| Low | 0.090175 | 0.19 | 15% | 2.5x on p |

---

## Revenue Erosion (S3 vs BAU)

See `s3_revenue_erosion_results.csv` for detailed projections. Key inputs:
- Grid reduction: HI=1,041 kWh/yr, MI=1,327 kWh/yr, LI=584 kWh/yr per SHS household
- Tariffs (2024 base): HI/MI=R3.50/kWh, LI=R2.06/kWh, 10% annual escalation

---

## Files Reference

| File | Purpose |
|---|---|
| `bass_diffusion_s3.py` | S3 Bass model (generates s3_bass_diffusion_results.csv) |
| `s3_bass_diffusion_results.csv` | S3 year-by-year adoption & capacity (2018-2050) |
| `revenue_erosion_s3.py` | Revenue erosion calculator |
| `s3_revenue_erosion_results.csv` | Revenue erosion output |
| `LEAP_BAU_implementation_guide.md` | BAU setup (prerequisite) |
