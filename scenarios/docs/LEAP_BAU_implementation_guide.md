# LEAP Implementation Guide: Updated BAU Scenario

## Overview

Step-by-step instructions for entering the **Updated BAU** scenario into the LEAP model (`capetown_07072025.leap`).

**Data Source (v3 — corrected 2026-03-16):**
- Income groups: LifeLine=Low, Domestic=Mid, HomeUser=High (tariff-based)
- Adoption rates from Biz's Mask2Former satellite detection pipeline
- Calibration: 2022-2023 only (>98% tariff coverage; 2020-21 excluded)
- System sizes: Mean from actual data (4.91/3.66/2.84 kW)
- Household counts: Sales Summaries .xlsm, SUMMATED SALES sheet
- Smooth backfill: Exponential interpolation from estimated 2018 values to 2022

**Key changes from Brian's original BAU:**

| Parameter | Brian's BAU | Updated BAU (v3) |
|-----------|-------------|-------------------|
| Income mapping | Postpaid=HI, Prepaid=MI | HomeUser=HI, Domestic=MI, LifeLine=LI |
| HI households | 158,743 | 309,402 |
| MI households | 168,040 | 150,534 |
| LI households | 306,998 | 172,697 |
| System sizes | 8/5/3 kW | 4.91/3.66/2.84 kW (mean) |
| BAU saturation | 50/50/0% | 25/15/3% |
| Calibration window | 2020-2023 | 2022-2023 only |
| Interp() range | 2024-2050 | 2018-2050 (smooth, no dips) |

**IMPORTANT:** These Interp() expressions cover the full 2018-2050 range, replacing Brian's original 2018-2023 historical values. This avoids the dip/discontinuity caused by different income group definitions.

---

## Step 1: Demand Side — High-Income (m=25%)

Navigate to: **Demand → Households → Electrified → High Income → Grid and SHS**

Set Activity Level (% of HH with SHS):
```
Interp(2018, 0.50, 2019, 0.88, 2020, 1.56, 2021, 2.74, 2022, 4.84, 2023, 7.29, 2024, 10.10, 2025, 13.10, 2026, 16.04, 2027, 18.66, 2028, 20.76, 2029, 22.30, 2030, 23.35, 2035, 24.89, 2040, 24.99, 2045, 25.00, 2050, 25.00)
```

Grid Only: `Remainder(100)`

---

## Step 2: Demand Side — Mid-Income (m=15%)

Navigate to: **Demand → Households → Electrified → Middle Income → Grid and SHS**

```
Interp(2018, 0.10, 2019, 0.22, 2020, 0.47, 2021, 1.01, 2022, 2.18, 2023, 3.28, 2024, 4.54, 2025, 5.93, 2026, 7.39, 2027, 8.84, 2028, 10.19, 2029, 11.37, 2030, 12.35, 2035, 14.59, 2040, 14.95, 2045, 14.99, 2050, 15.00)
```

Grid Only: `Remainder(100)`

---

## Step 3: Demand Side — Low-Income (m=3%, NEW: was 0% in Brian's BAU)

Navigate to: **Demand → Households → Electrified → Low Income**

Create **"Grid and SHS"** sub-branch if it doesn't exist.

```
Interp(2018, 0.00, 2019, 0.13, 2020, 0.26, 2021, 0.38, 2022, 0.51, 2023, 0.64, 2024, 0.78, 2025, 0.94, 2026, 1.10, 2027, 1.27, 2028, 1.44, 2029, 1.62, 2030, 1.79, 2035, 2.47, 2040, 2.81, 2045, 2.94, 2050, 2.98)
```

Grid Only: `Remainder(100)`

---

## Step 4: Supply Side — SSEG Capacity

Navigate to: **Transformation → Distributed Generation → SSEG**

Total SSEG capacity (MW, residential + commercial):
```
Interp(2018, 10, 2019, 18, 2020, 33, 2021, 60, 2022, 109, 2023, 165, 2024, 231, 2025, 303, 2026, 377, 2027, 445, 2028, 505, 2029, 553, 2030, 590, 2035, 687, 2040, 741, 2045, 792, 2050, 845)
```

Capacity factor: **19.6%** (SOEC 2021)

Note: 2018 calculated SSEG (10 MW) is lower than registered (19 MW) because registered includes commercial systems not captured in our residential model. By 2022-2023, Mask2Former detects unregistered residential systems, so calculated exceeds registered.

---

## Energy Intensity

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

## Verification

After entering values, press **F5** to run. Check:

1. **Activity levels**: "Grid Only" + "Grid and SHS" = 100% for each group
2. **Smooth curves**: No dips or discontinuities from 2018 to 2050
3. **BAU 2050 SSEG generation**: ~1,451 GWh (845 MW × 19.6% × 8,760h)
4. **Load shedding**: Compare unmet requirements vs Brian's original BAU

---

## Bass Model Parameters (BAU)

| Group | p | q | m (saturation) | Y0 (2023) |
|---|---|---|---|---|
| High | 0.047960 | 0.38 | 25% | 7.29% |
| Mid | 0.042203 | 0.30 | 15% | 3.28% |
| Low | 0.019909 | 0.19 | 3% | 0.64% |

---

## Backfill Methodology (2018-2022)

Since reliable data is only available for 2022-2023, the 2018-2022 period uses exponential interpolation:

| Group | 2018 anchor | 2022 data | Method |
|---|---|---|---|
| High | 0.50% | 4.84% | Exponential growth (x9.68 over 4 years) |
| Mid | 0.10% | 2.18% | Exponential growth (x21.8 over 4 years) |
| Low | 0.00% | 0.51% | Linear interpolation (near-zero start) |

2018 anchors are estimated from the overall SSEG registration trend (19 MW in 2018, mostly commercial + early HI adopters).

---

## Files Reference

| File | Purpose |
|---|---|
| `bass_diffusion_bau.py` | BAU Bass model (generates bau_bass_diffusion_results.csv) |
| `bau_bass_diffusion_results.csv` | BAU year-by-year adoption & capacity (2018-2050) |
