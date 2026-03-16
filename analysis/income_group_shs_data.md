# Income Group Classification & SHS Adoption Data

**Date:** March 16, 2026 (updated)
**Purpose:** Empirical data inputs for Bass diffusion model, segmented by residential income group.
**Version:** v2 — corrected SHS counts with full pipeline verification against Biz's data pipeline.

---

## 1. Income Group Definition

Residential households are classified into three income groups based on City of Cape Town electricity tariff categories:

| Income Group | Tariff Categories | Rationale |
|---|---|---|
| **Low** | LifeLine 1 60, LifeLine 2 25 (all sub-types: Formal, Informal, Indigent, Rebated, Backyarder, Tenant) | Subsidized tariff requiring means-testing (income or property value threshold). Free allocation of 25-60 kWh/month. |
| **Mid** | Domestic (all sub-types: Formal, Informal, Indigent, Rebated, Backyarder) | Standard residential tariff. No subsidy qualification required, moderate consumption levels. |
| **High** | HomeUser (Prepaid + Credit/Postpaid, including AMI variants) | High-consumption residential tariff. Larger homes, more appliances. Includes both prepaid and credit (postpaid) meter customers. |

**Notes:**
- Small Power Users (commercial) and Large Power Users (industrial) are excluded.
- SSEG (Small Scale Embedded Generation) customers are tracked separately.
- Sub-types (Formal, Informal, Indigent, etc.) are aggregated within each group.

### Data Sources
- **Tariff classification:** `trfname` field in `combined_02072026.parquet` (prepaid); `rate_category` in same file (postpaid)
- **Household counts:** Sales Summaries `.xlsm` files, `SUMMATED SALES` sheet (Credit + Prepaid combined, annual average)
- **SHS labels:** `shs_label_edit = 'PV_normal'` in `combined_02072026.parquet`. This is the **final output of Biz's pipeline** (step 5c), which includes: Mask2Former satellite image detection → building matching → cleaning assumptions (gap fill, forward extend) → SSEG registration merge → manual visual verification. See [Biz's repo](https://github.com/biz-yoder/EnergyTransitionDuringEnergyCrisisCapeTown) for full pipeline.
- **System sizes:** `Watt` field in the same parquet file. Calculated as `shs_area_m2 * 400W / 1.7m²` (~235 W/m²), with fallback to SSEG-registered `total_capacity_va` when area is unavailable.
- **Postpaid mapping:** For accounts with `trfname = NULL` (postpaid), `rate_category` is used: HOME/HOM/DOM variants → Mid; SPU/TOU/LPU/SSG(non-DOM) → High. No postpaid "Low" category exists.

---

## 2. Validation of Tariff-Based Income Grouping

Three independent metrics confirm the tariff-to-income mapping:

### 2a. Electricity Consumption (kWh/month)

| Income Group | Median kWh | Mean kWh | Unique Contracts |
|---|---:|---:|---:|
| Low | 206 | — | 125,199 |
| Mid | 311 | — | 124,952 |
| High | 425 | — | 169,097 |

Monotonic increase: Low (+51%) -> Mid (+37%) -> High.

### 2b. SHS Adoption Rate

| Income Group | SHS Adopters | Total Contracts | Adoption Rate |
|---|---:|---:|---|
| Low | 7 | 134,942 | 0.01% |
| Mid | 139 | 126,188 | 0.11% |
| High | 1,784 | 171,535 | 1.04% |

100x difference between Low and High, consistent with solar requiring capital investment.

### 2c. Property Values (Postpaid Subset, indirect)

| Solar Status | Median Property Value | N Contracts |
|---|---|---:|
| Non-SHS | R 2,350,000 | ~60,000 |
| SHS (solar) | R 3,800,000 | ~3,500 |

Property value tercile analysis (postpaid only, ~207K accounts):

| Tercile | Property Value Range | SHS Rate |
|---|---|---|
| Bottom 33% | < R 1.7M | 2.25% |
| Middle 33% | R 1.7M - R 3.06M | 5.39% |
| Top 33% | > R 3.06M | 11.88% |

### 2d. Solar Aerial Survey Cross-Check (2019 Census Income Codes)

| Income Group (Census) | Monthly Income Range | Share of PV Sites |
|---|---|---|
| Low (Code 2-5) | R 0 - R 3,200 | 3.3% |
| Mid (Code 6-7) | R 3,201 - R 12,800 | 15.9% |
| High (Code 8-10) | R 12,801+ | 77.0% |

---

## 3. Household Counts by Income Group (Annual)

Source: Sales Summaries `.xlsm`, `SUMMATED SALES` sheet. Values are 12-month average customer counts.

| Fiscal Year | Low | Mid | High | SSEG | Total Residential |
|---|---:|---:|---:|---:|---:|
| 2018/19 | 184,716 | 174,692 | 235,489 | 302 | 595,199 |
| 2019/20 | 168,108 | 159,865 | 276,767 | 423 | 605,163 |
| 2020/21 | 163,335 | 157,352 | 276,344 | 539 | 597,570 |
| 2021/22 | 164,841 | 156,798 | 286,767 | 692 | 609,098 |
| 2022/23 | 172,697 | 150,534 | 309,402 | 824 | 633,457 |

**Note:** Prior to 2017/18, "Domestic" and "HomeUser" had different classification criteria. Data before that year is not directly comparable.

---

## 4. SHS Adoption by Income Group (Annual)

Source: `combined_02072026.parquet`, `shs_label_edit = 'PV_normal'`, deduplicated by `contract_ID` per year.

### 4a. Full SHS Counts (All Accounts)

| Year | Total SHS (all accounts) |
|---|---:|
| 2020 | 6,563 |
| 2021 | 8,740 |
| 2022 | 11,886 |
| 2023 | 19,744 |

### 4b. SHS by Income Group (Mapped Residential Only)

| Year | Low | Mid | High | Mapped Residential | Unmapped Prepaid | Commercial |
|---|---:|---:|---:|---:|---:|---:|
| 2020 | 0 | 1,383 | 822 | 2,205 | 4,370 | — |
| 2021 | 351 | 2,820 | 4,986 | 8,157 | 5,071 | 399 |
| 2022 | 466 | 3,507 | 7,685 | 11,658 | 0 | 519 |
| 2023 | 613 | 5,354 | 13,754 | 19,721 | 0 | 797 |

**Data quality note:** In 2020, ALL prepaid accounts have `trfname = NULL`, so 4,370 SHS accounts (67% of total) cannot be assigned to an income group. In 2021, 5,071 prepaid SHS accounts (58%) remain unmapped. From 2022 onward, coverage is >98%.

### 4c. Adoption Rates (2022-2023 only, reliable years)

| Year | Low Rate | Mid Rate | High Rate |
|---|---|---|---|
| 2022 | 0.51% | 2.18% | 4.84% |
| 2023 | 0.64% | 3.28% | 7.29% |

### 4d. Recommendation for Bass Model

- **Use 2022-2023 for income-group-level fitting** (clean data, >98% coverage).
- **Use 2020-2023 total SHS counts** (Section 4a) for aggregate-level fitting if income group breakdown is not needed.
- **Do not use 2020-2021 income-group breakdowns** for calibration — the unmapped prepaid accounts make these unreliable.

---

## 5. SHS System Size by Income Group

Source: `combined_02072026.parquet`, `Watt` field for accounts with `shs_label_edit = 'PV_normal'`. Per-contract deduplicated (most recent observation).

| Income Group | P25 (kW) | Median (kW) | P75 (kW) | Mean (kW) |
|---|---:|---:|---:|---:|
| Low | 0.81 | 1.46 | 4.97 | 2.84 |
| Mid | 1.25 | 2.82 | 4.53 | 3.66 |
| High | 1.48 | 2.90 | 4.66 | 4.91 |

**Key observation:** Median system sizes (1.5-2.9 kW) are substantially smaller than previously assumed Bass model parameters (3-8 kW). Mid and High medians are very similar (~2.8-2.9 kW); the main difference is in the upper tail (High has more large systems, pulling the mean to 4.9 kW).

---

## 6. Prepaid vs Credit (Postpaid) Residential Split

Source: Sales Summaries `.xlsm`.

| Fiscal Year | Credit Residential | Prepaid Residential | Credit % |
|---|---:|---:|---|
| 2015/16 | 107,942 | 465,856 | 18.8% |
| 2018/19 | 88,476 | 506,723 | 14.9% |
| 2020/21 | 79,753 | 517,817 | 13.3% |
| 2022/23 | 69,404 | 564,053 | 10.9% |

Credit residential is declining (~5%/year) but has not been fully converted to prepaid. As of 2022/23, ~70K credit residential customers remain.

---

## 7. Pipeline Verification

The `combined_02072026.parquet` file has been verified as the **final output of Biz's data pipeline** (step 5c in [biz-yoder/EnergyTransitionDuringEnergyCrisisCapeTown](https://github.com/biz-yoder/EnergyTransitionDuringEnergyCrisisCapeTown)).

Evidence: file contains all 5c-stage fields (`Did not build`, `Built; NOT found by M2F`, `Built; found by M2F`, `total_capacity_va`, `installation_type`, `fake`, `start_year`, `has_shs`), confirming it includes SSEG registration merge and manual visual verification corrections.

SHS detection method: **Mask2Former** (satellite image semantic segmentation) detecting rooftop solar panels → spatial matching to Overture Maps building polygons → matching to electricity contract accounts → cleaning assumptions (single-year isolation removal, gap filling, forward extension to 2023) → SSEG registration cross-check with manual visual verification.

---

## 8. Limitations

1. **Tariff as income proxy:** Tariff category is an indirect proxy for income. Within-group income variation may be large, especially for Domestic (Mid).
2. **LifeLine eligibility gaps:** Some qualifying low-income households may not have applied for LifeLine tariff and are misclassified as Mid.
3. **SHS detection accuracy:** The `shs_label_edit` field is generated by Mask2Former satellite image segmentation, not from installation records. The pipeline includes manual visual verification for SSEG-registered accounts, but unregistered accounts rely solely on model predictions. False positives/negatives are possible.
4. **2020-2021 tariff data gap:** All prepaid accounts in 2020 and most in 2021 have `trfname = NULL`, preventing income group assignment. Income-group-level analysis is only reliable for 2022-2023.
5. **Postpaid coverage gap:** Property values are only available for ~10% of residential accounts (postpaid). Direct wealth-based validation is limited to this subset.
6. **Temporal alignment:** Sales Summary years are fiscal (July-June); parquet data years are calendar (Jan-Dec). Minor misalignment exists.
7. **Pre-2018 incompatibility:** Tariff category definitions changed around 2017/18. Historical data before this period uses different classification criteria.
8. **System size estimation:** `Watt` is derived from satellite-detected panel area (235 W/m²), not from inverter specifications or metered output. Actual capacity may differ.
