# Updated S3 Progressive Subsidy Scenario: Methodology and References

## 1. Overview

The Updated S3 Progressive Subsidy scenario models SHS adoption in Cape Town under an **income-scaled subsidy policy**, built on top of the Updated BAU. It replaces the old S3 which used Brian's original BAU as baseline (50% saturation, Postpaid/Prepaid income mapping, 8/5/3 kW system sizes).

**S3 Policy Design:**
- Low-income households receive the **largest** subsidy (p multiplied by 2.5x)
- Middle-income households receive a **moderate** subsidy (p multiplied by 1.5x)
- High-income households receive **no additional subsidy** (market-driven, same p as BAU)
- Higher saturation ceilings enabled by policy (30/25/15% vs BAU 25/15/3%)
- Policy divergence begins in **2024** — all 2018-2023 values identical to BAU

### 1.1 What Changed from Old S3

| Parameter | Old S3 | Updated S3 (v3) |
|---|---|---|
| **BAU baseline** | 30/20/0% saturation | 25/15/3% saturation |
| **S3 saturation** | 30/25/15% | 30/25/15% (unchanged) |
| **Income mapping** | Postpaid=HI, Prepaid=MI | HomeUser=HI, Domestic=MI, LifeLine=LI |
| **HH counts** | HI 158K, MI 168K, LI 307K | HI 309K, MI 150K, LI 173K |
| **System sizes** | 8/5/3 kW | 4.91/3.66/2.84 kW (measured mean) |
| **Calibration data** | 2020-2023 (4 points, unreliable years included) | 2022-2023 only (2 points, >98% coverage) |
| **Calibration method** | scipy curve_fit with HI only, then multipliers | 2-point algebraic on HI, then multipliers |
| **HI p value** | 0.0271 (old) | 0.036070 (updated) |
| **MI p value** | 0.0406 (1.5x old HI) | 0.054105 (1.5x updated HI) |
| **LI p value** | 0.0676 (2.5x old HI) | 0.090175 (2.5x updated HI) |
| **LI BAU baseline** | 0% (no SHS at all) | 0.64% (2023, satellite-detected) |
| **2018-2023 history** | From old BAU (different income groups) | Smooth backfill matching Updated BAU |

---

## 2. Relationship to Updated BAU

The Updated S3 is constructed as a **policy overlay** on the Updated BAU:

1. **Same historical data (2018-2023):** Both scenarios use identical adoption rates from Biz's Mask2Former data. The subsidy policy has not yet been implemented.
2. **Same calibration base:** HI Bass parameters are calibrated from the same 2022-2023 data.
3. **Divergence starts 2024:** S3 applies policy multipliers to p and raises saturation caps.
4. **Same household/system parameters:** HH counts, system sizes, energy intensity, growth rates are identical.

**What S3 changes relative to BAU:**

| Parameter | BAU | S3 | How |
|---|---|---|---|
| m (saturation) | 25/15/3% | 30/25/15% | Policy raises adoption ceiling |
| p (innovation) | Each group independent | HI calibrated, MI=1.5x, LI=2.5x | Subsidy accelerates adoption trigger |
| q (imitation) | 0.38/0.30/0.19 | 0.38/0.30/0.19 | Unchanged (peer effects same) |

---

## 3. Bass Diffusion Model

Same model as Updated BAU (see `Updated_BAU_methodology.md` Section 2).

**Discrete form:**
```
y_t = (m - Y_{t-1}) × [p + q × (Y_{t-1} / m)]
Y_t = Y_{t-1} + y_t
```

---

## 4. Historical Calibration Data

**Identical to Updated BAU** — same Mask2Former pipeline, same tariff-based income groups, same 2022-2023 window. See `Updated_BAU_methodology.md` Section 3 for full details.

| Year | High Income | Mid Income | Low Income |
|---|---|---|---|
| 2022 | 4.84% | 2.18% | 0.51% |
| 2023 | 7.29% | 3.28% | 0.64% |

---

## 5. Model Parameters and Their Sources

### 5.1 S3 Calibration Strategy

Unlike the Updated BAU (which calibrates p independently for each income group), the S3 scenario uses a **cascade approach**:

1. **Step 1:** Calibrate HI p from 2022-2023 data using S3's higher saturation (m=0.30)
2. **Step 2:** Apply policy multipliers to derive MI and LI p values
3. **Step 3:** Use literature q values (same as BAU)

**Why cascade?** The progressive subsidy policy doesn't have historical data — it hasn't been implemented. So MI and LI p values cannot be independently calibrated. Instead, HI (which receives no subsidy in S3) is calibrated from data, and MI/LI are derived by scaling HI's p by the subsidy multiplier.

### 5.2 Innovation Coefficient (p) — Calibration + Policy Multipliers

**Step 1: Calibrate HI p**

Same algebraic method as BAU, but with S3's saturation (m=0.30 instead of 0.25):

```
p_HI = (Y_2023 - Y_2022) / (m - Y_2022) - q × Y_2022 / m
p_HI = (0.0729 - 0.0484) / (0.30 - 0.0484) - 0.38 × 0.0484 / 0.30
p_HI = 0.036070
```

**Note:** HI p is lower in S3 (0.036070) than in BAU (0.047960) because S3's higher m (30% vs 25%) means the same observed growth requires less innovation pressure.

**Step 2: Apply policy multipliers**

| Income Group | p Value | Derivation |
|---|---|---|
| High | 0.036070 | Calibrated from data (no subsidy for HI) |
| Mid | 0.054105 | p_HI × **1.5** (moderate subsidy) |
| Low | 0.090175 | p_HI × **2.5** (largest subsidy) |

**Policy multiplier rationale:**
- **1.5x for MI:** Moderate subsidy (e.g., co-financing, low-interest loans, tax rebates) reduces the affordability barrier, increasing external adoption trigger
- **2.5x for LI:** Full or near-full subsidy (e.g., government-funded installation, community solar programs) makes SHS accessible to households with no capital
- These multipliers are **policy design assumptions**, not derived from cost-benefit analysis or empirical subsidy data

### 5.3 Imitation Coefficient (q) — From Literature

Same as BAU. Subsidy changes the external push (p), not the peer effect strength (q).

| Income Group | q Value | Source |
|---|---|---|
| High | 0.38 | Batista da Silva et al.; Schilling et al. 2009 |
| Mid | 0.30 | Schilling et al. 2009 |
| Low | 0.19 | Schilling et al. 2009 |

### 5.4 Market Saturation Cap (m) — Policy-Enhanced Ceilings

| Income Group | BAU m | S3 m | Policy Effect |
|---|---|---|---|
| High | 25% | 30% | +5pp: organic growth from favorable policy environment |
| Mid | 15% | 25% | +10pp: subsidy removes affordability barrier for additional 10% of HH |
| Low | 3% | 15% | +12pp: subsidy enables market entry for low-income HH |

**Rationale for S3 ceilings:**
- **HI 30%:** Modest increase over BAU. Favorable policy environment (streamlined permitting, net metering) encourages some marginal adopters.
- **MI 25%:** Subsidy covers down payment / financing gap, making SHS accessible to HH that could afford ongoing savings but not upfront cost.
- **LI 15%:** Full subsidy removes capital barrier, but structural constraints remain (informal housing ~15%, unsuitable roofs, tenure issues). 15% represents households in formal housing with suitable roofs.

### 5.5 Complete Parameter Summary

| Parameter | High Income | Mid Income | Low Income | Source |
|---|---|---|---|---|
| p (innovation) | 0.036070 | 0.054105 | 0.090175 | HI calibrated, MI/LI via multiplier |
| q (imitation) | 0.38 | 0.30 | 0.19 | Literature (fixed) |
| m (saturation) | 30% | 25% | 15% | Policy design assumption |
| Y0 (2023 start) | 7.29% | 3.28% | 0.64% | Mask2Former satellite data |
| Policy multiplier | 1.0x | 1.5x | 2.5x | Progressive subsidy design |

---

## 6. Household and System Parameters

**All identical to Updated BAU.** See `Updated_BAU_methodology.md` Section 5.

| Parameter | High | Mid | Low | Source |
|---|---|---|---|---|
| HH count (2023) | 309,402 | 150,534 | 172,697 | Sales Summaries |
| HH growth | 1.3% CAGR | 1.3% CAGR | 1.3% CAGR | IRP |
| System size (kW) | 4.91 | 3.66 | 2.84 | Mask2Former measured |
| Grid kWh/yr (SHS HH) | 5,492 | 5,020 | 3,303 | Final Report Table 8 |
| SHS kWh/yr (SHS HH) | 1,041 | 1,327 | 584 | Final Report Table 8 |
| Commercial multiplier | 1.25 | | | SSEG registration mix |
| Capacity factor | 19.6% | | | SOEC 2021 |

---

## 7. Backfill Methodology (2018-2022)

**Identical to Updated BAU.** S3 uses the same exponential backfill since the subsidy hasn't been implemented yet in 2018-2022. See `Updated_BAU_methodology.md` Section 6.

| Year | High | Mid | Low |
|---|---|---|---|
| 2018 | 0.50% | 0.10% | 0.00% |
| 2019 | 0.88% | 0.22% | 0.13% |
| 2020 | 1.56% | 0.47% | 0.26% |
| 2021 | 2.74% | 1.01% | 0.38% |
| 2022 | 4.84% | 2.18% | 0.51% |

---

## 8. Projection Results

### 8.1 SHS Adoption Rates (%)

| Year | S3 High | S3 Mid | S3 Low | BAU High | BAU Mid | BAU Low |
|---|---|---|---|---|---|---|
| 2018 | 0.50% | 0.10% | 0.00% | 0.50% | 0.10% | 0.00% |
| 2022 | 4.84% | 2.18% | 0.51% | 4.84% | 2.18% | 0.51% |
| 2023 | 7.29% | 3.28% | 0.64% | 7.29% | 3.28% | 0.64% |
| 2024 | 10.21% | 5.31% | 2.05% | 10.10% | 4.54% | 0.78% |
| 2025 | 13.48% | 7.63% | 3.56% | 13.10% | 5.93% | 0.94% |
| 2030 | 26.99% | 19.57% | 10.59% | 23.35% | 12.35% | 1.79% |
| 2035 | 29.76% | 24.20% | 13.92% | 24.89% | 14.59% | 2.47% |
| 2040 | 29.98% | 24.91% | 14.78% | 24.99% | 14.95% | 2.81% |
| 2050 | 30.00% | 25.00% | 14.99% | 25.00% | 15.00% | 2.98% |

**Key observations:**
- **2018-2023:** Identical (pre-policy)
- **2024 divergence:** Largest gap in LI (2.05% vs 0.78%), smallest in HI (10.21% vs 10.10%)
- **2030:** S3 LI is 10.59% vs BAU 1.79% — subsidy increases LI adoption by **5.9x**
- **2050:** All groups near saturation in both scenarios

### 8.2 Total SSEG Capacity (MW, including commercial ×1.25)

| Year | S3 SSEG (MW) | BAU SSEG (MW) | Difference |
|---|---|---|---|
| 2023 | 165 | 165 | 0 |
| 2025 | 339 | 303 | +36 MW |
| 2030 | 780 | 590 | +190 MW |
| 2035 | 954 | 687 | +267 MW |
| 2040 | 1,036 | 741 | +295 MW |
| 2050 | 1,182 | 845 | +337 MW |

### 8.3 Annual SSEG Generation (2050)

- S3: 1,182 MW × 19.6% × 8,760h = **2,028 GWh/yr**
- BAU: 845 MW × 19.6% × 8,760h = **1,451 GWh/yr**
- Difference: **+577 GWh/yr** (+40%)

---

## 9. Sensitivity Analysis

Parameters p and q varied by **±30%** across 5 scenarios. By 2050, all income groups approach saturation in all scenarios:

| Income Group | Low Scenario (2050) | Base (2050) | High Scenario (2050) |
|---|---|---|---|
| High | 30.0% | 30.0% | 30.0% |
| Mid | 24.9% | 25.0% | 25.0% |
| Low | 14.8% | 15.0% | 15.0% |

**Key finding:** Same as BAU — the saturation cap (m) is the binding constraint, not diffusion speed. The most impactful uncertain parameter is **m itself**, not p or q.

---

## 10. Known Limitations and Uncertainties

### 10.1 Parameter Confidence

| Parameter | Confidence | Issue |
|---|---|---|
| Historical adoption (2022-2023) | **High** | Mask2Former data, >98% coverage |
| Household counts | **High** | Municipal Sales Summaries |
| System sizes (mean) | **High** | Satellite-measured panel area |
| q values (literature) | **Medium** | Global, not Cape Town-specific |
| p calibration (HI) | **Medium** | 2-point calibration, no R2 possible |
| m values (saturation) | **Low-Medium** | Policy design assumptions |
| Policy multipliers (1.5x, 2.5x) | **Low** | No cost-benefit analysis or empirical subsidy data |
| 2018-2021 backfill | **Low** | Estimated, no ground truth |

### 10.2 Methodological Limitations

1. **Policy multipliers are not tied to specific subsidy amounts:** The model does not specify how much the subsidy costs or its structure (grants, loans, tax credits). The 1.5x/2.5x multipliers are a design assumption.
2. **Only 2 calibration points:** Same limitation as BAU. No goodness-of-fit metric possible with algebraic calibration.
3. **Cascade calibration:** MI and LI p values are derived from HI's calibrated p, not from their own observed data. This assumes the subsidy effect is proportional to the baseline adoption pressure, which may not hold.
4. **No behavioral response modeling:** The model assumes subsidy directly translates to faster adoption (higher p). In reality, subsidy uptake depends on awareness, administrative burden, trust in government programs, etc.
5. **Constant peer effects:** q is fixed across scenarios and time. Subsidized adoption may generate different peer dynamics than market-driven adoption.
6. **Saturation caps as policy targets:** The 30/25/15% ceilings assume the subsidy successfully overcomes structural barriers. If informal housing or tenure issues persist, actual saturation may be lower.
7. **No supply-side constraints:** The model assumes solar panel supply, installer capacity, and grid infrastructure can support the projected growth.

---

## 11. References

### Primary Data Sources

1. **Yoder, N. (2025).** "Inequality in Resilience: Understanding Household Electricity Consumption During Load Shedding in Cape Town." Dissertation. — *Mask2Former satellite detection; SHS adoption 2020-2023.*

2. **City of Cape Town.** Sales Summaries `.xlsm`, SUMMATED SALES sheet. — *Household counts by tariff.*

3. **Energy Modeling Team Final Report** (Finkle, Evans, Shah, Mutua B., Spring 2025). — *Energy intensity (Table 8), SSEG capacity (Table 16).*

4. **Cape Town SOEC 2021.** — *SSEG capacity factor (19.6%).*

5. **South Africa IRP.** — *HH growth rate (1.3% CAGR).*

### Bass Diffusion Model Literature

6. **Bass, F. M. (1969).** "A New Product Growth for Model Consumer Durables." *Management Science*, 15(5).

7. **Batista da Silva, P. et al.** Market diffusion of household PV systems using Bass model.

8. **Schilling, M. A. & Esmundo, M. (2009).** "Technology S-curves in renewable energy alternatives." *Energy Policy*, 37(5).

### Policy and Planning

9. **City of Cape Town & SEA (2015).** "Energy Scenarios for Cape Town" — *Original 50% saturation source (Brian's BAU baseline).*

10. **RES4Africa Foundation.** — *Low-income SHS self-sufficiency baseline.*

---

## 12. File Inventory

| File | Description |
|---|---|
| `bass_diffusion_s3.py` | S3 Bass model implementation (generates all S3 outputs) |
| `s3_bass_diffusion_results.csv` | Year-by-year projection data (2018-2050) |
| `s3_adoption_curves.png` | Adoption rate plots by income group |
| `s3_total_capacity.png` | Stacked residential SHS capacity |
| `s3_sensitivity_analysis.png` | ±30% sensitivity analysis |
| `revenue_erosion_s3.py` | Revenue erosion calculator |
| `s3_revenue_erosion_results.csv` | Revenue erosion output |
| `LEAP_S3_implementation_guide.md` | Step-by-step LEAP input instructions |
| `Updated_BAU_methodology.md` | BAU methodology (prerequisite reading) |
