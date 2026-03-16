# LEAP Implementation Guide: BAU & S3 Progressive Subsidy Scenarios

## Overview

This guide provides step-by-step instructions for building both the **BAU** and **S3 Progressive Subsidy** scenarios in the LEAP model (`capetown_07072025.leap`).

**Data Source (v3 — corrected 2026-03-16):**
- Income groups: LifeLine=Low, Domestic=Mid, HomeUser=High (tariff-based)
- Adoption rates from Biz's Mask2Former satellite detection pipeline
- Calibration: 2022-2023 only (>98% tariff coverage; 2020-21 excluded)
- System sizes: Mean from actual data (4.91/3.66/2.84 kW)
- Household counts: Sales Summaries .xlsm, SUMMATED SALES sheet
- Smooth backfill: Exponential interpolation from estimated 2018 values to 2022

**Key changes from old model:**

| Parameter | Old Model | Corrected (v3) |
|-----------|-----------|----------------|
| Income mapping | Postpaid=HI, Prepaid=MI | HomeUser=HI, Domestic=MI, LifeLine=LI |
| HI households | 158,743 | 309,402 |
| MI households | 168,040 | 150,534 |
| LI households | 306,998 | 172,697 |
| System sizes | 8/5/3 kW | 4.91/3.66/2.84 kW (mean) |
| BAU saturation | 30/20/0% | 25/15/3% |
| S3 saturation | 30/25/15% | 30/25/15% (unchanged) |
| Calibration window | 2020-2023 | 2022-2023 only |
| Interp() range | 2024-2050 | 2018-2050 (smooth, no dips) |

**Prerequisites:**
- LEAP/NEMO software installed (Windows)
- `capetown_07072025.leap` model file open in LEAP

**IMPORTANT:** These Interp() expressions cover the full 2018-2050 range, replacing Brian's original 2018-2023 historical values with our corrected income group definitions. This avoids the dip/discontinuity that occurs when only entering 2024+ data on top of Brian's different classification.

---

## Part A: BAU Scenario

### Step A1: Demand Side — High-Income

Navigate to: **Demand → Households → Electrified → High Income → Grid and SHS**

Set Activity Level (% of HH with SHS):
```
Interp(2018, 0.50, 2019, 0.88, 2020, 1.56, 2021, 2.74, 2022, 4.84, 2023, 7.29, 2024, 10.10, 2025, 13.10, 2026, 16.04, 2027, 18.66, 2028, 20.76, 2029, 22.30, 2030, 23.35, 2035, 24.89, 2040, 24.99, 2045, 25.00, 2050, 25.00)
```

Grid Only: `Remainder(100)`

### Step A2: Demand Side — Mid-Income

Navigate to: **Demand → Households → Electrified → Middle Income → Grid and SHS**

```
Interp(2018, 0.10, 2019, 0.22, 2020, 0.47, 2021, 1.01, 2022, 2.18, 2023, 3.28, 2024, 4.54, 2025, 5.93, 2026, 7.39, 2027, 8.84, 2028, 10.19, 2029, 11.37, 2030, 12.35, 2035, 14.59, 2040, 14.95, 2045, 14.99, 2050, 15.00)
```

Grid Only: `Remainder(100)`

### Step A3: Demand Side — Low-Income (NEW: was 0% in old BAU)

Navigate to: **Demand → Households → Electrified → Low Income**

Create **"Grid and SHS"** sub-branch if it doesn't exist.

```
Interp(2018, 0.00, 2019, 0.13, 2020, 0.26, 2021, 0.38, 2022, 0.51, 2023, 0.64, 2024, 0.78, 2025, 0.94, 2026, 1.10, 2027, 1.27, 2028, 1.44, 2029, 1.62, 2030, 1.79, 2035, 2.47, 2040, 2.81, 2045, 2.94, 2050, 2.98)
```

Grid Only: `Remainder(100)`

### Step A4: Supply Side — BAU SSEG Capacity

Navigate to: **Transformation → Distributed Generation → SSEG**

Total SSEG capacity (residential + commercial):
```
Interp(2018, 10, 2019, 18, 2020, 33, 2021, 60, 2022, 109, 2023, 165, 2024, 231, 2025, 303, 2026, 377, 2027, 445, 2028, 505, 2029, 553, 2030, 590, 2035, 687, 2040, 741, 2045, 792, 2050, 845)
```

Capacity factor: **19.6%** (SOEC 2021)

Note: 2018 calculated SSEG (10 MW) is lower than registered (19 MW) because registered includes commercial systems not captured in our residential model. By 2022-2023, Mask2Former detects unregistered residential systems, so calculated exceeds registered.

---

## Part B: S3 Progressive Subsidy Scenario

### Step B1: Create the S3 Scenario

1. **Analysis → Manage Scenarios** → Add
2. **Name:** `S3 Progressive Subsidy`
3. **Inherit from:** `Business-As-Usual (BAU)`
4. Only values that differ from BAU need to be entered

### Step B2: Demand Side — High-Income (S3, m=30%)

Navigate to: **High Income → Grid and SHS** (in S3 scenario)

From `s3_bass_diffusion_results.csv` (p=0.036070, q=0.38):
```
Interp(2018, 0.50, 2019, 0.88, 2020, 1.56, 2021, 2.74, 2022, 4.84, 2023, 7.29, 2024, 10.21, 2025, 13.48, 2026, 16.90, 2027, 20.17, 2028, 23.04, 2029, 25.32, 2030, 26.99, 2035, 29.76, 2040, 29.98, 2045, 30.00, 2050, 30.00)
```

Grid Only: `Remainder(100)`

### Step B3: Demand Side — Mid-Income (S3, m=25%, p=1.5x HI)

From `s3_bass_diffusion_results.csv` (p=0.054105, q=0.30):
```
Interp(2018, 0.10, 2019, 0.22, 2020, 0.47, 2021, 1.01, 2022, 2.18, 2023, 3.28, 2024, 5.31, 2025, 7.63, 2026, 10.16, 2027, 12.77, 2028, 15.31, 2029, 17.61, 2030, 19.57, 2035, 24.20, 2040, 24.91, 2045, 24.99, 2050, 25.00)
```

Grid Only: `Remainder(100)`

### Step B4: Demand Side — Low-Income (S3, m=15%, p=2.5x HI)

From `s3_bass_diffusion_results.csv` (p=0.090175, q=0.19):
```
Interp(2018, 0.00, 2019, 0.13, 2020, 0.26, 2021, 0.38, 2022, 0.51, 2023, 0.64, 2024, 2.05, 2025, 3.56, 2026, 5.10, 2027, 6.64, 2028, 8.09, 2029, 9.42, 2030, 10.59, 2035, 13.92, 2040, 14.78, 2045, 14.96, 2050, 14.99)
```

Grid Only: `Remainder(100)`

### Step B5: Supply Side — S3 SSEG Capacity

Total SSEG = residential capacity × 1.25 (commercial estimate):
```
Interp(2018, 10, 2019, 18, 2020, 33, 2021, 60, 2022, 110, 2023, 165, 2024, 246, 2025, 339, 2026, 439, 2027, 539, 2028, 632, 2029, 713, 2030, 780, 2035, 954, 2040, 1036, 2045, 1107, 2050, 1182)
```

---

## Energy Intensity (Both Scenarios)

From Energy Modeling Team Report Table 8 (base year 2018):

| Income Group | Total kWh/HH/yr | Grid kWh | SHS kWh | SSEG Share |
|---|---|---|---|---|
| High-Income | 6,533 | 5,492 | 1,041 | 16% |
| Mid-Income | 6,347 | 5,020 | 1,327 | 21% |
| Low-Income | 3,887 | 3,303 | 584 | 15% |

Energy intensity annual change: **-0.6% CAGR** (to achieve 0.7% total demand growth with 1.3% HH growth, per IRP)

---

## Household Counts

Source: Sales Summaries .xlsm, 2022/23 fiscal year. Growth: 1.3% CAGR.

| Year | High | Mid | Low | Total |
|---|---|---|---|---|
| 2018 | 289,698 | 140,942 | 161,697 | 592,337 |
| 2023 | 309,402 | 150,534 | 172,697 | 632,633 |
| 2025 | 317,499 | 154,473 | 177,216 | 649,188 |
| 2030 | 338,680 | 164,779 | 189,039 | 692,497 |
| 2040 | 385,375 | 187,497 | 215,102 | 787,975 |
| 2050 | 438,509 | 213,349 | 244,760 | 896,617 |

Proportions (fixed): High=48.8%, Mid=23.8%, Low=27.3%

---

## BAU vs S3 Comparison

| Year | BAU SSEG (MW) | S3 SSEG (MW) | Difference |
|---|---|---|---|
| 2025 | 303 | 339 | +36 MW |
| 2030 | 590 | 780 | +190 MW |
| 2035 | 687 | 954 | +267 MW |
| 2040 | 741 | 1,036 | +295 MW |
| 2050 | 845 | 1,182 | +337 MW |

---

## Verification

After entering values, press **F5** to run. Check:

1. **Activity levels**: "Grid Only" + "Grid and SHS" = 100% for each group
2. **Smooth curves**: No dips or discontinuities from 2018 to 2050
3. **BAU 2050 SSEG generation**: ~1,451 GWh (845 MW × 19.6% × 8,760h)
4. **S3 2050 SSEG generation**: ~2,028 GWh (1,182 MW × 19.6% × 8,760h)
5. **Load shedding**: S3 should show reduced unmet requirements vs BAU
6. **Sankey diagrams**: Compare energy flows 2024 vs 2050

---

## Bass Model Parameters

### BAU (no subsidy)

| Group | p | q | m | Y0 (2023) |
|---|---|---|---|---|
| High | 0.047960 | 0.38 | 25% | 7.29% |
| Mid | 0.042203 | 0.30 | 15% | 3.28% |
| Low | 0.019909 | 0.19 | 3% | 0.64% |

### S3 (progressive subsidy)

| Group | p | q | m | Policy multiplier |
|---|---|---|---|---|
| High | 0.036070 | 0.38 | 30% | 1.0x (no subsidy) |
| Mid | 0.054105 | 0.30 | 25% | 1.5x on p |
| Low | 0.090175 | 0.19 | 15% | 2.5x on p |

---

## Backfill Methodology (2018-2022)

Since reliable data is only available for 2022-2023, the 2018-2022 period uses exponential interpolation:

| Group | 2018 anchor | 2022 data | Method |
|---|---|---|---|
| High | 0.50% | 4.84% | Exponential growth (×9.68 over 4 years) |
| Mid | 0.10% | 2.18% | Exponential growth (×21.8 over 4 years) |
| Low | 0.00% | 0.51% | Linear interpolation (near-zero start) |

2018 anchors are estimated from the overall SSEG registration trend (19 MW in 2018, mostly commercial + early HI adopters).

---

## Files Reference

| File | Purpose |
|---|---|
| `bass_diffusion_bau.py` | BAU Bass model (generates bau_bass_diffusion_results.csv) |
| `bass_diffusion_s3.py` | S3 Bass model (generates s3_bass_diffusion_results.csv) |
| `revenue_erosion_s3.py` | Revenue erosion calculator |
| `bau_bass_diffusion_results.csv` | BAU year-by-year adoption & capacity (2018-2050) |
| `s3_bass_diffusion_results.csv` | S3 year-by-year adoption & capacity (2018-2050) |
| `s3_revenue_erosion_results.csv` | Revenue erosion output |
