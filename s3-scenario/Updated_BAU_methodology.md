# Updated BAU Scenario: Methodology and References

## 1. Overview

The Updated BAU (Business-As-Usual) scenario models Solar Home System (SHS) adoption in Cape Town under **no policy intervention** — pure market-driven adoption. It replaces Brian Mutua's original BAU, which used General Household Survey data and a 50% saturation target from a 2015 Cape Town policy scenario.

The key improvement is replacing registration-based SSEG data with **satellite-detected SHS data** from Biz Yoder's Mask2Former pipeline, which captures unregistered installations and provides ~3x more accurate adoption counts.

### 1.1 What Changed from Brian's Original BAU

| Parameter | Brian's Original BAU | Updated BAU (v3) |
|---|---|---|
| **SHS data source** | GHS 2023 survey + SSEG registration + goal-seek | Mask2Former satellite detection (2022-2023) |
| **Income mapping** | Postpaid=HI, Prepaid=MI (billing method) | HomeUser=HI, Domestic=MI, LifeLine=LI (tariff-based) |
| **HI households** | 158,743 | 309,402 |
| **MI households** | 168,040 | 150,534 |
| **LI households** | 306,998 | 172,697 |
| **System sizes** | 8/5/3 kW (assumption) | 4.91/3.66/2.84 kW (measured mean) |
| **Saturation** | 50%/50%/0% | 25%/15%/3% |
| **Saturation source** | Cape Town 2015 Energy Scenarios report | Structural constraint analysis |
| **LI adoption** | 0% (no SHS at all) | 0.64% baseline (2023), 3% ceiling |
| **Calibration window** | 2020-2023 (4 points, includes unreliable years) | 2022-2023 only (2 points, >98% coverage) |
| **Calibration method** | scipy curve_fit (4 points) | Algebraic 2-point calibration |
| **2018-2023 history** | Goal-seek from SSEG registration data | Exponential backfill from estimated 2018 anchors |

---

## 2. Bass Diffusion Model

### 2.1 Mathematical Formulation

**Discrete form (used for year-by-year projection):**

```
y_t = (m - Y_{t-1}) × [p + q × (Y_{t-1} / m)]
Y_t = Y_{t-1} + y_t
```

Where:
- `m` = market saturation cap (maximum fraction of households that will ever adopt SHS without policy)
- `p` = innovation coefficient (external influence: marketing, awareness, load shedding motivation)
- `q` = imitation coefficient (internal influence: peer effects, neighborhood visibility)
- `Y_t` = cumulative adoption fraction at time t
- `y_t` = new adopters as fraction of total market in period t

### 2.2 Intuition

The Bass model produces an **S-curve**:
- **Early phase:** Adoption slow, driven mainly by `p` (individual awareness, load shedding frustration)
- **Growth phase:** Adoption accelerates as `q × (Y/m)` grows (more neighbors install → stronger peer effect)
- **Saturation phase:** Adoption slows as `(m - Y)` shrinks (remaining addressable market decreases)

---

## 3. Historical Calibration Data

### 3.1 Data Source: Yoder (2025) Mask2Former Pipeline

**Primary source:** Yoder, N. (2025). "Inequality in Resilience: Understanding Household Electricity Consumption During Load Shedding in Cape Town." Dissertation data pipeline output: `combined_02072026.parquet`.

**Pipeline steps:**
1. **Mask2Former** satellite image semantic segmentation → detect rooftop solar panels
2. Spatial matching to **Overture Maps** building polygons
3. Matching to **electricity contract accounts** (via building → meter address)
4. **Cleaning:** single-year isolation removal, gap filling, forward extension to 2023
5. **SSEG registration cross-check** with manual visual verification
6. Final label: `shs_label_edit = 'PV_normal'`

**Why not SSEG registration data?** Approximately **two-thirds (~67%) of SHS installations in Cape Town are unregistered** with the municipal SSEG program. Satellite detection captures all installations regardless of registration, yielding more accurate adoption counts.

### 3.2 Income Group Classification (Tariff-Based)

Source: `trfname` field in `combined_02072026.parquet` (prepaid); `rate_category` for postpaid.

| Income Group | Tariff Categories | Rationale |
|---|---|---|
| **High** | HomeUser (Prepaid + Credit/Postpaid, incl AMI) | High-consumption residential; larger homes, more appliances |
| **Mid** | Domestic (all sub-types) | Standard residential; no subsidy qualification |
| **Low** | LifeLine 1&2 (all sub-types: Formal, Informal, Indigent, Rebated, Backyarder, Tenant) | Subsidized tariff; means-tested |

**Why tariff-based, not billing method?** Brian's original classification (Postpaid=HI, Prepaid=MI) conflated billing method with income. Many high-consumption HomeUser customers use prepaid meters, causing them to be misclassified as middle-income. Tariff category directly reflects consumption level and subsidy eligibility.

**Validation:** The tariff-to-income mapping was cross-validated against 4 independent metrics (see `analysis/income_group_shs_data.md`):
1. Electricity consumption: Low 206 kWh/mo < Mid 311 < High 425 (monotonic)
2. SHS adoption rate: Low 0.01% < Mid 0.11% < High 1.04% (100x range)
3. Property values: SHS homes median R3.8M vs non-SHS R2.35M
4. Census income codes: 77% of PV sites in high-income census areas

### 3.3 Why Only 2022-2023?

| Year | Tariff Coverage | Unmapped Prepaid | Usable? |
|---|---|---|---|
| 2020 | ~33% | 4,370 SHS (67% of total) | No |
| 2021 | ~42% | 5,071 SHS (58% of total) | No |
| 2022 | >98% | 0 | **Yes** |
| 2023 | >98% | 0 | **Yes** |

In 2020-2021, all/most prepaid accounts had `trfname = NULL`, making income group assignment impossible for the majority of SHS installations. Only 2022-2023 have >98% coverage.

### 3.4 Historical Adoption Rates (Calibration Data)

| Year | High Income | Mid Income | Low Income |
|---|---|---|---|
| 2022 | 4.84% (7,685 SHS / ~159K HH) | 2.18% (3,507 SHS / ~161K HH) | 0.51% (466 SHS / ~91K HH) |
| 2023 | 7.29% (13,754 SHS / ~189K HH) | 3.28% (5,354 SHS / ~163K HH) | 0.64% (613 SHS / ~96K HH) |

Source: `combined_02072026.parquet`, `shs_label_edit = 'PV_normal'`, deduplicated by `contract_ID` per year.

---

## 4. Model Parameters and Their Sources

### 4.1 Imitation Coefficient (q) — From Literature

Fixed from solar PV adoption literature, not calibrated from Cape Town data. With only 2 data points, fitting both p and q simultaneously is mathematically impossible (system is underdetermined).

| Income Group | q Value | Rationale |
|---|---|---|
| High | 0.38 | Strong peer effects in affluent neighborhoods; visible rooftop installations |
| Mid | 0.30 | Moderate peer effects |
| Low | 0.19 | Weaker but non-zero peer effects |

**Literature sources:**
- Batista da Silva, P. et al. — Market diffusion of household PV systems using Bass model
- Schilling, M. A. & Esmundo, M. (2009). "Technology S-curves in renewable energy alternatives." *Energy Policy*, 37(5), 1767-1781.

### 4.2 Innovation Coefficient (p) — 2-Point Algebraic Calibration

With exactly 2 data points and q fixed, p is solved directly from the Bass equation:

```
Y_2023 - Y_2022 = (m - Y_2022) × [p + q × (Y_2022 / m)]

Solving for p:
p = (Y_2023 - Y_2022) / (m - Y_2022) - q × Y_2022 / m
```

| Income Group | p Value | Derivation |
|---|---|---|
| High | 0.047960 | Algebraic from 4.84% → 7.29% with m=0.25, q=0.38 |
| Mid | 0.042203 | Algebraic from 2.18% → 3.28% with m=0.15, q=0.30 |
| Low | 0.019909 | Algebraic from 0.51% → 0.64% with m=0.03, q=0.19 |

**Note:** Unlike the old S3 model which calibrated only HI and derived MI/LI via multipliers, the Updated BAU calibrates each income group independently from its own observed data.

### 4.3 Market Saturation Cap (m) — Structural Constraint Analysis

Brian's original 50% came from the "Embedded Solar PV Scenario" in Cape Town's 2015 Energy Scenarios update — a **policy planning target**, not an empirical estimate.

The updated saturations are derived from **structural constraints** that limit SHS adoption even in the long run:

**High Income: m = 25%**
- ~30% renters (cannot install)
- ~15% unsuitable roofs (shading, orientation, structural issues)
- ~10% apartments/complexes (body corporate restrictions)
- ~20% no motivation (already reliable backup: generators, batteries, or low load shedding impact)
- Residual addressable: ~25%

**Mid Income: m = 15%**
- ~40% affordability barrier (SHS cost R60K-R150K without subsidy)
- ~25% renters
- ~15% roof access/suitability issues
- ~5% informal housing
- Residual addressable: ~15%

**Low Income: m = 3%**
- ~70% affordability barrier (no access to financing without subsidy)
- ~15% informal housing (no permanent roof structure)
- ~12% tenure uncertainty
- Residual addressable: ~3% (exceptional early adopters, community-funded pilots)

### 4.4 Complete Parameter Summary

| Parameter | High Income | Mid Income | Low Income | Source |
|---|---|---|---|---|
| p (innovation) | 0.047960 | 0.042203 | 0.019909 | 2-point algebraic calibration |
| q (imitation) | 0.38 | 0.30 | 0.19 | Literature (fixed) |
| m (saturation) | 25% | 15% | 3% | Structural constraint analysis |
| Y0 (2023 start) | 7.29% | 3.28% | 0.64% | Mask2Former satellite data |

---

## 5. Household and System Parameters

### 5.1 Household Counts

Source: Sales Summaries `.xlsm`, SUMMATED SALES sheet (12-month average customer counts).

| Income Group | Tariff | 2022/23 HH Count |
|---|---|---|
| High | HomeUser | 309,402 |
| Mid | Domestic | 150,534 |
| Low | LifeLine 1&2 | 172,697 |
| **Total** | | **632,633** |

**Projection:** 1.3% CAGR from South Africa Integrated Resource Plan (IRP).

**Proportions (fixed):** High=48.8%, Mid=23.8%, Low=27.3%

### 5.2 Average SHS System Size

Source: `Watt` field in `combined_02072026.parquet`. Calculated as `shs_area_m2 × 400W / 1.7m2` (~235 W/m2), with fallback to SSEG-registered `total_capacity_va` when area unavailable.

| Income Group | P25 (kW) | Median (kW) | P75 (kW) | Mean (kW) |
|---|---|---|---|---|
| High | 1.48 | 2.90 | 4.66 | **4.91** |
| Mid | 1.25 | 2.82 | 4.53 | **3.66** |
| Low | 0.81 | 1.46 | 4.97 | **2.84** |

**Mean** is used for capacity projections (accounts for large-system tail in HI).

**Key observation:** Actual system sizes (median 1.5-2.9 kW) are substantially smaller than Brian's assumptions (8/5/3 kW). The difference is because Mask2Former detects all systems including small ones, while SSEG registration is biased toward larger systems.

### 5.3 Energy Intensity

Source: Energy Modeling Team Final Report, Table 8 (unchanged from Brian's model).

| Income Group | Total kWh/HH/yr | Grid Share | SHS Share | Grid kWh | SHS kWh |
|---|---|---|---|---|---|
| High | 6,533 | 84% | 16% | 5,492 | 1,041 |
| Mid | 6,347 | 79% | 21% | 5,020 | 1,327 |
| Low | 3,887 | 85% | 15% | 3,303 | 584 |

### 5.4 SSEG Capacity Factor

**Value:** 19.6%
**Source:** Cape Town State of Energy and Carbon Report (SOEC) 2021.

### 5.5 Commercial Multiplier

**Value:** 1.25 (residential capacity × 1.25 = total SSEG including commercial)
**Rationale:** Commercial SSEG estimated at ~25% of residential capacity based on SSEG registration mix.

---

## 6. Backfill Methodology (2018-2022)

### 6.1 Problem

LEAP base year is 2018. Reliable income-group SHS data only exists for 2022-2023. Brian's 2018-2023 values use different income group definitions, so they cannot be directly connected to our 2024+ projections (this caused the "dip" artifact in LEAP charts).

### 6.2 Solution: Exponential Interpolation

For each income group, estimate a 2018 anchor and interpolate exponentially to the observed 2022 value:

```
y(t) = y_2018 × (y_2022 / y_2018)^((t - 2018) / 4)
```

For Low Income (y_2018 = 0), linear interpolation is used instead.

| Group | 2018 Anchor | 2022 Observed | Method | Rationale |
|---|---|---|---|---|
| High | 0.50% | 4.84% | Exponential (×9.68 over 4 years) | Early adopters pre-load-shedding |
| Mid | 0.10% | 2.18% | Exponential (×21.8 over 4 years) | Very few early adopters |
| Low | 0.00% | 0.51% | Linear | Near-zero start, no exponential base |

### 6.3 2018 Anchor Estimation

The 2018 anchors (HI=0.50%, MI=0.10%, LI=0.00%) are estimates based on:
- Cape Town registered SSEG was 19 MW in 2018 (Table 16), mostly commercial + large residential
- SHS adoption was in very early phase pre-load-shedding crisis (Stage 6 started Feb 2023)
- Mask2Former data not available before 2020

### 6.4 Backfill Results

| Year | High | Mid | Low |
|---|---|---|---|
| 2018 | 0.50% | 0.10% | 0.00% |
| 2019 | 0.88% | 0.22% | 0.13% |
| 2020 | 1.56% | 0.47% | 0.26% |
| 2021 | 2.74% | 1.01% | 0.38% |
| 2022 | 4.84% | 2.18% | 0.51% |

---

## 7. Projection Results

### 7.1 SHS Adoption Rates (%)

| Year | High Income | Mid Income | Low Income |
|---|---|---|---|
| 2018 | 0.50% | 0.10% | 0.00% |
| 2022 | 4.84% | 2.18% | 0.51% |
| 2023 | 7.29% | 3.28% | 0.64% |
| 2025 | 13.10% | 5.93% | 0.94% |
| 2030 | 23.35% | 12.35% | 1.79% |
| 2035 | 24.89% | 14.59% | 2.47% |
| 2040 | 24.99% | 14.95% | 2.81% |
| 2050 | 25.00% | 15.00% | 2.98% |

### 7.2 Total SSEG Capacity (MW, including commercial ×1.25)

| Year | Residential (MW) | Total SSEG (MW) |
|---|---|---|
| 2018 | 8 | 10 |
| 2023 | 132 | 165 |
| 2025 | 243 | 303 |
| 2030 | 472 | 590 |
| 2040 | 593 | 741 |
| 2050 | 676 | 845 |

### 7.3 Annual SSEG Generation (2050)

845 MW × 19.6% CF × 8,760 h = **1,451 GWh/yr**

---

## 8. Known Limitations and Uncertainties

### 8.1 Parameter Confidence

| Parameter | Confidence | Issue |
|---|---|---|
| Historical adoption (2022-2023) | **High** | Mask2Former satellite data, >98% coverage |
| Household counts | **High** | Municipal Sales Summaries |
| System sizes (mean) | **High** | Measured from satellite-detected panel area |
| q values (literature) | **Medium** | Global solar PV literature, not Cape Town-specific |
| p calibration | **Medium** | Only 2 data points; no goodness-of-fit metric possible |
| m values (saturation) | **Low-Medium** | Structural analysis, not empirically verified |
| 2018-2021 backfill | **Low** | Estimated anchors, no ground truth |

### 8.2 Methodological Limitations

1. **Only 2 calibration points (2022-2023):** Insufficient to assess goodness-of-fit (R2 requires >=3 points). The algebraic calibration perfectly fits both points but provides no confidence interval.
2. **Saturation caps are assumptions:** The 25/15/3% values are based on qualitative structural analysis, not regression or survey data. If actual saturation is higher (e.g., 40% for HI), the model significantly underestimates long-term adoption.
3. **2018-2021 backfill is synthetic:** No income-group-level ground truth exists before 2022. The exponential interpolation is a smooth approximation, not observed data.
4. **Load shedding not explicitly modeled:** The Bass model's p coefficient implicitly captures load shedding motivation, but the model does not separately account for load shedding stages or frequency changes.
5. **Constant q over time:** Peer effects are assumed constant; in reality they may strengthen as adoption becomes more visible.
6. **Tariff as income proxy:** Some low-income HH may not have applied for LifeLine tariff and are misclassified as Mid.
7. **System size estimation:** `Watt` is derived from satellite-detected panel area (~235 W/m2), not inverter specs or metered output.

---

## 9. References

### Primary Data Sources

1. **Yoder, N. (2025).** "Inequality in Resilience: Understanding Household Electricity Consumption During Load Shedding in Cape Town." Dissertation. — *Mask2Former satellite detection pipeline; SHS adoption rates 2020-2023; data file: `combined_02072026.parquet`.*

2. **City of Cape Town.** Sales Summaries `.xlsm` files, SUMMATED SALES sheet. — *Household counts by tariff category (2018-2023).*

3. **Energy Modeling Team Final Report** (Finkle, Evans, Shah, Mutua B., Spring 2025). — *Energy intensity (Table 8), SSEG historical capacity (Table 16), tariff-income mapping (Table 6).*

4. **Cape Town State of Energy and Carbon Report (SOEC), 2021.** — *SSEG capacity factor (19.6%).*

5. **South Africa Integrated Resource Plan (IRP).** — *Household growth rate (1.3% CAGR).*

### Bass Diffusion Model Literature

6. **Bass, F. M. (1969).** "A New Product Growth for Model Consumer Durables." *Management Science*, 15(5), 215-227.

7. **Batista da Silva, P. et al.** Market diffusion of household PV systems using Bass diffusion model. — *Solar PV p and q ranges.*

8. **Schilling, M. A. & Esmundo, M. (2009).** "Technology S-curves in renewable energy alternatives." *Energy Policy*, 37(5), 1767-1781. — *q values for renewable energy.*

### Saturation Cap Source (Brian's Original)

9. **City of Cape Town & Sustainable Energy Africa (2015).** "Energy Scenarios for Cape Town: Exploring the Implications of Different Energy Futures for the City of Cape Town up to 2040." — *Brian's 50% saturation target came from the "Embedded Solar PV Scenario" in this report. We replaced this with structural constraint analysis.*

---

## 10. File Inventory

| File | Description |
|---|---|
| `bass_diffusion_bau.py` | BAU Bass model implementation (generates all BAU outputs) |
| `bau_bass_diffusion_results.csv` | Year-by-year projection data (2018-2050) |
| `bau_adoption_curves.png` | Adoption rate plots by income group |
| `bau_total_capacity.png` | Stacked residential SHS capacity |
| `LEAP_BAU_implementation_guide.md` | Step-by-step LEAP input instructions |
| `../analysis/income_group_shs_data.md` | Source data documentation and validation |
