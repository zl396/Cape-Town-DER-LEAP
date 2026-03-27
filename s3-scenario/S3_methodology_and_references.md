# S3 Progressive Subsidy Scenario: Methodology and References

## 1. Overview

The S3 Progressive Subsidy scenario models Solar Home System (SHS) adoption in Cape Town under an income-scaled subsidy policy. Low-income households receive the largest subsidy, middle-income households receive a moderate subsidy, and high-income households receive no additional incentive beyond the market baseline.

The core modeling tool is the **Bass Diffusion Model**, a widely used technology adoption framework that captures both external influences (policy, advertising) and internal influences (peer effects, word-of-mouth).

---

## 2. Bass Diffusion Model

### 2.1 Mathematical Formulation

**Discrete form (used for projection):**

```
y_t = (m - Y_{t-1}) × [p + q × (Y_{t-1} / m)]
Y_t = Y_{t-1} + y_t
```

**Continuous form (used for calibration/curve fitting):**

```
F(t) = m × [1 - e^(-(p+q)t)] / [1 + (q/p) × e^(-(p+q)t)]
```

Where:
- `m` = market saturation cap (maximum fraction of households that will ever adopt)
- `p` = innovation coefficient (external influence: policy push, subsidies, advertising)
- `q` = imitation coefficient (internal influence: peer effects, word-of-mouth)
- `Y_t` = cumulative adoption fraction at time t
- `y_t` = new adoption fraction in period t

### 2.2 Intuition

The Bass model produces an **S-curve**:
- **Early phase:** Adoption is slow, driven mainly by `p` (policy/external push)
- **Growth phase:** Adoption accelerates as `q × (Y/m)` grows (more neighbors have adopted → stronger peer effect)
- **Saturation phase:** Adoption slows as `(m - Y)` shrinks (remaining market space decreases)

---

## 3. Historical Calibration Data

### 3.1 Data Source: Yoder (2025) Aerial Imagery

**Primary source:** Yoder, N. (2025). "Inequality in Resilience: Understanding Household Electricity Consumption During Load Shedding in Cape Town." Dissertation, Chapter 3, Table 3.

**Method:** Mask2Former deep learning model applied to high-resolution aerial imagery (2020-2023) to detect SHS panel installations on rooftops.

**Why this data?** Approximately **two-thirds (~67%) of SHS installations in Cape Town are unregistered** with the municipal SSEG program. Traditional SSEG registration data massively undercounts actual adoption, particularly for middle-income households. Yoder's aerial detection captures all installations regardless of registration status, yielding ~3x more accurate estimates.

**Key discrepancy discovered:**
- Middle-income 2023 adoption: **0.18%** (old SSEG registration data) vs **4.0%** (Yoder aerial data) — a **20x difference**
- High-income 2023 adoption: **8.0%** (old) vs **8.6%** (Yoder) — relatively close

### 3.2 Historical Adoption Rates

| Year | High-Income (Postpaid) | Middle-Income (Prepaid) | Low-Income |
|------|----------------------|------------------------|------------|
| 2020 | 3.1% | 1.2% | 0% |
| 2021 | 4.1% | 1.6% | 0% |
| 2022 | 5.5% | 2.4% | 0% |
| 2023 | 8.6% | 4.0% | 0% |

**Income group mapping:**
- **High-Income** = Postpaid / credit metering customers (HomeUser tariff)
- **Middle-Income** = Prepaid / token metering customers (Domestic tariff)
- **Low-Income** = LifeLine 1/2 tariff customers (no observed SHS adoption)

Source: Yoder (2025), Table 3; tariff classification from City of Cape Town metering data via Energy Modeling Team Final Report, Table 7.

---

## 4. Model Parameters and Their Sources

### 4.1 Imitation Coefficient (q) — From Literature

The q values are **fixed from solar PV adoption literature**, not calibrated from Cape Town data. This is because with only 4 data points (2020-2023), fitting both p and q simultaneously yields q ≈ 0, which is unrealistic (a known limitation of Bass model calibration with limited early-phase data).

| Income Group | q Value | Rationale |
|-------------|---------|-----------|
| High-Income | 0.38 | Strong peer effects in affluent neighborhoods; higher visibility of installations |
| Middle-Income | 0.30 | Moderate peer effects |
| Low-Income | 0.19 | Weaker but non-zero peer effects; enhanced by community programs |

**Literature sources for q values:**
- Batista da Silva, P. et al. — Market diffusion of household PV systems using Bass diffusion model
- Mejia, J. (2024). "Spatiotemporal Estimation of Rooftop PV Adoption"
- Schilling, M. A. & Esmundo, M. (2009). "Technology S-curves in renewable energy alternatives: Analysis and implications for industry and government." *Energy Policy*, 37(5), 1767-1781.

**General literature range:** p for solar PV: 0.001–0.03 (annual); q for solar PV: 0.3–0.6 (annual).

### 4.2 Innovation Coefficient (p) — Calibrated + Policy Multipliers

**Step 1: Calibrate High-Income p from historical data**

Using `scipy.optimize.curve_fit` in **hybrid mode** (q fixed at 0.38, m fixed at 0.30):
- Input: Yoder 2020-2023 high-income adoption rates
- Output: **p_HI ≈ 0.0271**
- Goodness of fit: R² = 0.508, reasonable given only 4 data points

**Step 2: Derive Middle/Low-Income p using policy multipliers**

| Income Group | p Value | Derivation |
|-------------|---------|------------|
| High-Income | 0.0271 | Calibrated from Yoder data |
| Middle-Income | 0.0406 | p_HI × **1.5** (moderate subsidy effect) |
| Low-Income | 0.0676 | p_HI × **2.5** (largest subsidy effect) |

**Policy multiplier rationale:** Larger subsidies for lower-income groups increase external influence (p), accelerating the initial adoption trigger. The specific multiplier values (1.5x and 2.5x) are **policy design assumptions** reflecting the progressive subsidy structure. They are not derived from empirical data or cost-benefit analysis.

### 4.3 Market Saturation Cap (m) — User-Specified Policy Targets

| Income Group | BAU m | S3 m | Change |
|-------------|-------|------|--------|
| High-Income | 30% | 30% | No change (no additional subsidy) |
| Middle-Income | 20% | 25% | +5pp (moderate subsidy increases ceiling) |
| Low-Income | 0% | 15% | +15pp (largest subsidy enables market entry) |

**Source:** Described in code as "conservative estimates per user specification." These represent **policy ambition targets**, not empirically derived market potential estimates. They reflect:
- Physical constraints (roof suitability, orientation, structural capacity)
- Economic constraints (affordability even with subsidy)
- Grid integration limits (maximum safe SSEG penetration)

### 4.4 Initial Adoption (Y0) — From Yoder 2023 Data

| Income Group | Y0 (2023 baseline) |
|-------------|-------------------|
| High-Income | 8.6% |
| Middle-Income | 4.0% |
| Low-Income | 0% |

### 4.5 Complete Parameter Summary

| Parameter | High-Income | Middle-Income | Low-Income | Source |
|-----------|------------|--------------|------------|--------|
| p (innovation) | 0.0271 | 0.0406 | 0.0676 | Calibrated / policy multiplier |
| q (imitation) | 0.38 | 0.30 | 0.19 | Literature (fixed) |
| m (saturation) | 30% | 25% | 15% | User specification |
| Y0 (2023 start) | 8.6% | 4.0% | 0% | Yoder (2025) |

---

## 5. Household and System Parameters

### 5.1 Household Counts

Source: Energy Modeling Team Final Report, Table 7; City of Cape Town tariff-based classification.

| Income Group | 2023 Households |
|-------------|----------------|
| High-Income | 158,743 |
| Middle-Income | 168,040 |
| Low-Income | 306,998 |

**Projection:** 1.3% CAGR from IRP (Integrated Resource Plan).

### 5.2 Average SHS System Size

| Income Group | System Size |
|-------------|------------|
| High-Income | 8 kW |
| Middle-Income | 5 kW |
| Low-Income | 3 kW |

**Note:** Income group SHS validation data (`analysis/income_group_shs_data.md`) indicates actual median system sizes may be smaller (1.5–2.9 kW). The values above are model assumptions.

### 5.3 Energy Intensity

Source: Energy Modeling Team Final Report, Table 8.

| Income Group | Grid Only (kWh/HH/yr) | Grid+SHS Grid portion | Grid+SHS SHS portion | SHS Self-Sufficiency |
|-------------|----------------------|----------------------|---------------------|---------------------|
| High-Income | 6,533 | 5,492 | 1,041 | 16% |
| Middle-Income | 6,347 | 5,020 | 1,326 | 21% |
| Low-Income | 3,887 | 3,303 | 584 | 15% |

Low-income SHS self-sufficiency (15%) is based on the RES4Africa baseline for smaller 3 kW systems.

### 5.4 SSEG Capacity Factor

**Value:** 19.6%

**Source:** Cape Town State of Energy and Carbon Report (SOEC) 2021.

---

## 6. Projection Results

### 6.1 SHS Adoption Rates (%)

| Year | High-Income | Middle-Income | Low-Income |
|------|------------|--------------|------------|
| 2023 | 8.6% | 4.0% | 0% |
| 2024 | 8.6% | 4.0% | 0% |
| 2025 | 11.1% | 5.3% | 0.4% |
| 2030 | 24.8% | 14.7% | 3.2% |
| 2035 | 29.4% | 22.3% | 7.5% |
| 2040 | 30.0% | 24.5% | 11.5% |
| 2045 | 30.0% | 24.9% | 13.7% |
| 2050 | 30.0% | 25.0% | 14.6% |

### 6.2 Total Residential SHS Capacity (MW)

| Year | High-Income | Middle-Income | Low-Income | Total Residential |
|------|------------|--------------|------------|------------------|
| 2023 | 109 | 34 | 0 | 143 |
| 2030 | 344 | 135 | 33 | 512 |
| 2040 | 474 | 257 | 132 | 863 |
| 2050 | 540 | 298 | 191 | 1,028 |

### 6.3 Total SSEG Capacity (with Commercial)

Commercial SSEG estimated at ~30% of BAU SSEG capacity, growing at 8% annually.

| Year | Residential SHS (MW) | Commercial SSEG (MW) | Total SSEG (MW) |
|------|---------------------|---------------------|-----------------|
| 2024 | ~145 | ~39 | ~184 |
| 2030 | ~512 | ~54 | ~566 |
| 2040 | ~863 | ~117 | ~980 |
| 2050 | ~1,028 | ~253 | ~1,281 |

---

## 7. Sensitivity Analysis

Parameters p and q varied by **±30%** across 5 scenarios:
- Baseline (calibrated values)
- High p + High q (+30% both)
- Low p + Low q (-30% both)
- High p + Low q (mixed)
- Low p + High q (mixed)

**Key finding:** By 2050, all income groups approach their saturation cap (m), making long-term results **insensitive** to ±30% parameter variation. The market saturation ceiling is the binding constraint, not the exact diffusion speed.

---

## 8. Calibration Methodology

### 8.1 Three Available Modes

| Mode | Description | When to Use |
|------|------------|------------|
| **Hybrid** (recommended) | Fix q from literature, calibrate p from data | Default; best for limited data (4 points) |
| Data-only | Fit both p and q from data | When >10 data points available |
| Default | Use literature defaults, no calibration | Fallback when scipy unavailable |

### 8.2 Why Hybrid Mode?

With only 4 annual data points (2020-2023) in the early adoption phase, a data-only calibration typically yields q ≈ 0 (no imitation effect). This is a known artifact of Bass model calibration with limited data — the early exponential growth can be explained entirely by p without needing q. The hybrid approach constrains q to a plausible literature range and solves for p, producing more realistic long-term projections.

---

## 9. Known Limitations and Uncertainties

### 9.1 Parameter Uncertainty

| Parameter | Confidence | Issue |
|-----------|-----------|-------|
| Historical adoption (Yoder) | **High** | Empirical aerial imagery data; ~3x more accurate than registration |
| Household counts | **High** | From municipal records (tariff-based) |
| q values (literature) | **Medium** | Based on global solar PV literature, not Cape Town-specific |
| p calibration (HI) | **Medium** | R² = 0.508; only 4 data points |
| m values (saturation caps) | **Low-Medium** | Policy design assumptions, not empirically derived |
| Policy multipliers (1.5x, 2.5x) | **Low** | No cost-benefit analysis or subsidy quantification |
| System sizes (8/5/3 kW) | **Medium** | Actual medians may be 1.5–2.9 kW |

### 9.2 Methodological Limitations

1. **Income group classification** is based on tariff categories (indirect income proxy), not actual household income
2. **Low-income adoption is entirely assumed** — no historical data exists; the 0% baseline and 15% ceiling are policy targets
3. **Policy multipliers are not tied to specific subsidy amounts** — the model does not specify the cost or structure of the progressive subsidy
4. **Peer effects (q) assumed constant over time** — in reality, peer influence may change as adoption grows
5. **No storage/battery modeling** — SHS capacity factor is applied uniformly; temporal mismatch with evening load shedding is not captured in the Bass model itself

### 9.3 Validation

- High-income calibration validated against Yoder (2025) observed 2023 data
- Income group classification cross-validated against 4 independent metrics: electricity consumption, SHS adoption rate, property values, and 2019 Census income codes (see `analysis/income_group_shs_data.md`)
- Revenue erosion estimates validated against Yoder's observed 2023 revenue impact (~0.2% of residential sales)

---

## 10. References

### Primary Data Sources

1. **Yoder, N. (2025).** "Inequality in Resilience: Understanding Household Electricity Consumption During Load Shedding in Cape Town." Dissertation, Chapter 3. — *Primary source for historical SHS adoption rates (2020-2023) via Mask2Former aerial imagery detection.*

2. **Energy Modeling Team Final Report.** — *Household counts (Table 7), energy intensity parameters (Table 8), SSEG capacity data (Table 16).*

3. **Cape Town State of Energy and Carbon Report (SOEC), 2021.** — *SSEG capacity factor (19.6%).*

4. **South Africa Integrated Resource Plan (IRP).** — *Household growth rate (1.3% CAGR).*

### Bass Diffusion Model Literature

5. **Bass, F. M. (1969).** "A New Product Growth for Model Consumer Durables." *Management Science*, 15(5), 215-227. — *Original Bass diffusion model.*

6. **Batista da Silva, P. et al.** Market diffusion of household PV systems using Bass diffusion model. — *Solar PV-specific p and q ranges.*

7. **Mejia, J. (2024).** "Spatiotemporal Estimation of Rooftop PV Adoption." — *PV adoption modeling methodology.*

8. **Schilling, M. A. & Esmundo, M. (2009).** "Technology S-curves in renewable energy alternatives: Analysis and implications for industry and government." *Energy Policy*, 37(5), 1767-1781. — *Renewable energy technology diffusion parameters.*

### Supporting Analysis

9. **RES4Africa Foundation.** — *Low-income SHS self-sufficiency baseline (15% for 3 kW systems).*

10. **City of Cape Town.** Metering and tariff classification data. — *Income group classification via tariff categories (LifeLine, Domestic, HomeUser).*

---

## 11. File Inventory

| File | Description |
|------|-------------|
| `bass_diffusion_s3.py` | Main Bass diffusion model implementation and calibration |
| `generate_excel.py` | Generates `S3_scenario_assumptions.xlsx` for LEAP input |
| `revenue_erosion_s3.py` | Revenue erosion analysis under S3 |
| `LEAP_S3_implementation_guide.md` | Step-by-step LEAP model input instructions |
| `S3_scenario_assumptions.xlsx` | Excel workbook with adoption rates, capacity, energy parameters |
| `s3_bass_diffusion_results.csv` | Year-by-year projection data (2020-2050) |
| `s3_adoption_curves.png` | Adoption rate visualization by income group |
| `s3_total_capacity.png` | Stacked capacity visualization |
| `s3_sensitivity_analysis.png` | ±30% sensitivity analysis visualization |
| `s3_revenue_erosion.png` | Revenue erosion over time |
| `s3_avoided_generation.png` | Avoided grid generation |
