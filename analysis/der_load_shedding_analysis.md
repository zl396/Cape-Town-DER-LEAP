# Cape Town DER Potential to Mitigate Load Shedding: A Systems Analysis

**ESM-01 Energy System Modeler Analysis**  
**Date:** March 2, 2026  
**Scenario:** S3 Progressive Subsidy (Bass Diffusion Model)

---

## Executive Summary

This analysis evaluates the potential of Distributed Energy Resources (DER) to mitigate load shedding in Cape Town under the S3 Progressive Subsidy scenario. **The critical finding is that temporal mismatch between solar generation and load shedding schedules fundamentally limits DER effectiveness without battery storage.**

### Key Findings

1. **Temporal Mismatch Dominates**: Evening load shedding (5-9pm) coincides with only ~12.5% solar capacity factor, creating a severe mismatch. Morning load shedding (6-9am) achieves ~30% CF overlap.

2. **Storage is Transformative**: Battery storage increases effective evening DER capacity from 72 MW to 292 MW by 2030—a 4× improvement.

3. **Household Resilience Remains Limited**: Only ~10.8% of households can island during load shedding, concentrated in high-income areas with battery storage.

4. **System-Level Impact by 2030**: With storage, DER can cover ~29% of Cape Town's Stage 4 morning burden and ~49% of evening burden.

5. **Not About Total Capacity**: The question isn't "how much DER capacity exists?" but "how much DER is available during load shedding hours with islanding capability?"

---

## 1. Methodology

### 1.1 Load Shedding Characterization

**Eskom Load Shedding Stages:**
- Stage 1: 1,000 MW national
- Stage 2: 2,000 MW national
- Stage 3: 3,000 MW national
- Stage 4: 4,000 MW national
- ... up to Stage 8: 8,000 MW national

**Typical Schedule:**
- **Duration**: 2-4 hour rotating blocks (avg 2.5 hours)
- **Peak Times**:
  - Morning: 6:00-9:00 AM (3 hours)
  - Evening: 5:00-9:00 PM (4 hours)
- **Cape Town Share**: ~15% of national load shedding burden

**Historical Context:**
- 2022-2024: South Africa experienced the worst load shedding on record
- Stage 4-6 was common, with frequent escalations to Stage 6
- Evening load shedding particularly severe during winter months

### 1.2 DER Capacity Projections (S3 Progressive Subsidy)

| Year | Residential SHS (MW) | Total with Commercial (MW) | Household Count | % with Solar |
|------|----------------------|----------------------------|-----------------|--------------|
| 2024 | 104 | 159 | 641,000 | ~16% |
| 2030 | 522 | 576 | 692,000 | ~25% |
| 2040 | 893 | 1,010 | 783,000 | ~33% |
| 2050 | 1,033 | 1,286 | 897,000 | ~38% |

**Income Group Distribution:**
- **High Income**: 30% saturation, 8 kW avg, 70% battery adoption
- **Middle Income**: 25% saturation, 5 kW avg, 40% battery adoption
- **Low Income**: 15% saturation, 3 kW avg, 10% battery adoption

### 1.3 Solar Generation Patterns

**Hourly Capacity Factors (Cape Town typical day):**
```
Hour  | CF    | Hour  | CF
------|-------|-------|-----
00-05 | 0.00  | 12-13 | 0.90
06    | 0.10  | 13-14 | 0.85
07    | 0.30  | 14-15 | 0.75
08    | 0.50  | 15-16 | 0.65
09    | 0.65  | 16-17 | 0.50
10    | 0.75  | 17    | 0.30
11    | 0.85  | 18    | 0.15
                19-23 | 0.00-0.05
```

**Critical Insight**: Peak midday CF (~85-90%) does NOT coincide with peak load shedding times (6-9am, 5-9pm).

### 1.4 Temporal Overlap Calculation

**Morning Load Shedding (6-9am):**
- Average solar CF: 30.0%
- Moderate overlap—solar is ramping up
- Effective DER availability: ~30% of installed capacity

**Evening Load Shedding (5-9pm):**
- Average solar CF: 12.5%
- SEVERE mismatch—solar is declining/dark
- Effective DER availability: ~13% of installed capacity WITHOUT storage

**Combined Peak Load Shedding:**
- Average solar CF: 19.6% (weighted by hours)
- Matches annual average CF by coincidence, but hides temporal distribution

---

## 2. Results

### 2.1 Effective DER Capacity During Load Shedding

#### Without Battery Storage

| Year | Total DER (MW) | Morning Effective (MW) | Evening Effective (MW) | Peak Combined (MW) |
|------|----------------|------------------------|------------------------|--------------------|
| 2024 | 159 | 47.7 | 19.9 | 37.5 |
| 2030 | 576 | 172.8 | 72.0 | 135.4 |
| 2040 | 1,010 | 303.0 | 126.3 | 237.2 |
| 2050 | 1,286 | 385.8 | 160.8 | 302.1 |

**Key Observation**: Without storage, evening capacity is only 42% of morning capacity due to temporal mismatch.

#### With Battery Storage (50% system penetration, 45% round-trip utilization)

| Year | Total DER (MW) | Morning Effective (MW) | Evening Effective (MW) | Peak Combined (MW) |
|------|----------------|------------------------|------------------------|--------------------|
| 2024 | 159 | 47.7 | 80.7 | 67.8 |
| 2030 | 576 | 172.8 | 292.3 | 245.7 |
| 2040 | 1,010 | 303.0 | 512.6 | 430.9 |
| 2050 | 1,286 | 385.8 | 652.6 | 548.9 |

**Key Observation**: Storage increases evening capacity by 4.1× (2030), enabling daytime solar surplus to cover evening load shedding.

### 2.2 Household-Level Resilience Analysis

**Islanding Requirements:**
1. Solar PV system installed
2. Battery storage (≥5 kWh for 2.5-hour Stage 4 outage)
3. Inverter with islanding capability

**Islanding-Capable Households:**

| Year | Total Households | Islanding Capable | % of Total | Can Ride Stage 4 |
|------|------------------|-------------------|------------|------------------|
| 2024 | 641,000 | 69,466 | 10.8% | 69,466 (100%) |
| 2030 | 692,000 | 75,064 | 10.8% | 75,064 (100%) |
| 2040 | 783,000 | 85,413 | 10.9% | 85,413 (100%) |
| 2050 | 897,000 | 97,190 | 10.8% | 97,190 (100%) |

**Income Distribution of Islanding Capability:**
- **High Income**: ~7.4% of total households (52% of high-income households)
- **Middle Income**: ~2.7% of total households (24% of middle-income households)
- **Low Income**: ~0.4% of total households (3.8% of low-income households)

**Critical Equity Concern**: Islanding capability is heavily concentrated in high-income households, exacerbating load shedding inequality.

### 2.3 System-Level Impact on Cape Town Load Shedding

**Cape Town Load Shedding Burden by Stage:**
- Stage 1: 150 MW (15% of 1,000 MW national)
- Stage 2: 300 MW
- Stage 3: 450 MW
- Stage 4: 600 MW
- Stage 6: 900 MW
- Stage 8: 1,200 MW

**DER Coverage of Cape Town's Stage 4 Burden (600 MW):**

| Year | Morning Coverage (%) | Evening Coverage (%) | Notes |
|------|----------------------|----------------------|-------|
| 2024 | 8.0% | 13.4% | Minimal system relief |
| 2030 | 28.8% | 48.7% | Approaching significant relief |
| 2040 | 50.5% | 85.4% | Can reduce Stage 4 → Stage 1-2 in evening |
| 2050 | 64.3% | 108.8% | Can eliminate Stage 4 burden in evening |

**Interpretation:**
- By 2040, DER with storage can reduce evening Stage 4 to Stage 1
- By 2050, DER can fully cover evening Stage 4 burden
- Morning coverage lags behind due to lower storage benefit
- Grid architecture limits: islanding households don't reduce aggregate grid burden unless they also reduce peak demand

### 2.4 Sensitivity Analysis

**Battery Storage Penetration:**
- **Baseline (50% penetration)**: Results shown above
- **Low (30% penetration)**: Evening 2030 capacity drops to 220 MW (-25%)
- **High (70% penetration)**: Evening 2030 capacity rises to 364 MW (+25%)

**Solar Capacity Factor Variation:**
- **Summer (CF +15%)**: Morning improves to 34.5%, evening to 14.4%
- **Winter (CF -25%)**: Morning drops to 22.5%, evening to 9.4%
- **Critical finding**: Winter CF reduction precisely when load shedding is worst

**Household Load Assumptions:**
- **Conservative (2 kW avg)**: Current assumption, 10.8% can island
- **Optimistic (1.5 kW avg)**: 15.2% can island with same battery capacity
- **Pessimistic (3 kW avg)**: 7.1% can island (low-income households excluded)

---

## 3. Policy Implications

### 3.1 Storage is Non-Negotiable for Load Shedding Mitigation

**Finding**: Without battery storage, DER provides only 25-40% of its potential load shedding relief.

**Recommendations:**
1. **Subsidize battery storage** alongside solar PV in S3 Progressive Subsidy
2. **Mandate storage for new installations**: Require ≥5 kWh battery for incentive eligibility
3. **Retrofit programs**: Target existing solar systems for battery additions
4. **Financing mechanisms**: Low-interest loans for storage, separate from solar PV loans

### 3.2 Address Equity and Cross-Subsidization Erosion

**Finding**: Islanding capability is concentrated in high-income households (68% of total), while low-income households remain grid-dependent.

**Risks:**
- Load shedding inequality worsens
- High-income defection from grid → revenue erosion → tariff death spiral
- Cross-subsidization base collapses (high-income pay above-cost rates)

**Recommendations:**
1. **Means-tested storage subsidies**: 80% subsidy for low-income, 40% for middle-income
2. **Community battery storage**: Municipal installations serving multiple low-income households
3. **Grid defection tax/fee**: Prevent full grid defection by high-income islanders
4. **Lifeline tariff protection**: Ensure low-income tariffs remain affordable despite revenue erosion

### 3.3 Prioritize Islanding-Capable Inverters

**Finding**: Not all solar systems can island during grid outages. Many grid-tied inverters shut down for safety.

**Recommendations:**
1. **Regulatory standards**: Update inverter requirements to include islanding capability
2. **Retrofit incentives**: Subsidize inverter upgrades for existing systems
3. **Consumer education**: Inform solar customers that grid-tied systems ≠ backup power

### 3.4 Optimize Load Shedding Schedules Around Solar Availability

**Finding**: Current load shedding schedules prioritize demand reduction during peaks (5-9pm), precisely when solar is unavailable.

**Innovative Recommendation:**
1. **Shift load shedding to midday (11am-2pm)** when solar CF is 75-90%
2. **Trade-off**: Residential inconvenience vs. industrial disruption
3. **Benefit**: DER-rich areas could avoid load shedding entirely, creating incentive for adoption
4. **Challenge**: Requires coordination with Eskom and municipal utilities

### 3.5 Monitor and Prevent Utility Death Spiral

**Finding**: Revenue erosion is complex and interacts with cross-subsidization structure.

**Next Steps (Part 2 of this analysis):**
1. Calculate annual revenue loss from DER adoption (using Cape Town tariff structure)
2. Model tariff increases needed to maintain revenue neutrality
3. Analyze cross-subsidization erosion as high-income adopt DER
4. Compare with international case studies (Australia, California, Hawaii)

---

## 4. Limitations and Future Work

### 4.1 Limitations

1. **Historical load shedding data**: Analysis uses typical schedules, not actual 2022-2024 load shedding events
2. **Solar CF assumptions**: Based on typical Cape Town curve; actual CF varies by location, season, weather
3. **Battery behavior**: Simplified model assumes 50% penetration and 45% round-trip utilization; actual dispatch is more complex
4. **Grid architecture**: Assumes islanding households don't reduce aggregate grid load; in reality, some behind-the-meter reduction occurs
5. **Demand growth**: Does not model electricity demand growth vs. DER growth race

### 4.2 Future Work

1. **Empirical validation**: Analyze actual load shedding events (2022-2024) using 15-minute resolution data
2. **LEAP integration**: Incorporate these findings into LEAP energy system model
3. **Revenue erosion analysis**: Part 2 of this analysis (see Section 3.5)
4. **Spatial analysis**: Map DER adoption vs. load shedding severity by Cape Town area
5. **Industrial/commercial DER**: Analyze commercial SSEG mitigation potential separately

---

## 5. Conclusion

**The potential of DER to mitigate load shedding in Cape Town is significant but heavily conditional on battery storage deployment.** Without storage, DER provides minimal relief during evening load shedding—precisely when households need it most. With 50% battery storage penetration, DER can reduce Stage 4 evening load shedding by 49% in 2030 and eliminate it entirely by 2050.

However, **household-level resilience remains inequitable**, with only ~11% of households able to island during load shedding, concentrated in high-income areas. This creates a two-tier electricity system: islanding-capable high-income households vs. grid-dependent low/middle-income households.

**Policy must prioritize:**
1. Battery storage subsidies (especially for low/middle-income)
2. Islanding-capable inverter standards
3. Equity mechanisms to prevent load shedding inequality
4. Revenue erosion mitigation to avoid utility death spiral

**The answer to "Can DER mitigate load shedding?" is:**  
*"Yes, but only with storage, only during certain hours, and only for households wealthy enough to afford islanding systems—unless policy intervenes."*

---

## References

1. Eskom (2024). Load Shedding Stages and Schedules. https://loadshedding.eskom.co.za/
2. City of Cape Town (2024). Load-shedding and Outages. https://www.capetown.gov.za/
3. Cape Town DER-LEAP Bass Diffusion Model (S3 Progressive Subsidy Scenario)
4. Energy Modeling Team Final Report (2026)
5. Individual Policy Report: Zhenghao Lin (Spring 2026)
6. South Africa Energy Sector: 2022-2024 Load Shedding Statistics

---

## Appendices

### Appendix A: Python Analysis Scripts
See `load_shedding_mitigation_analysis.py` for full calculation methodology and assumptions.

### Appendix B: Detailed JSON Results
See `projections_detailed.json` for granular results by year, income group, and load shedding stage.

### Appendix C: CSV Summary
See `projections_summary.csv` for tabular results suitable for import into LEAP or other models.
