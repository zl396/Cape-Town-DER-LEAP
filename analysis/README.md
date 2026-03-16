# Cape Town DER Load Shedding Mitigation Analysis

**ESM-01 Energy System Modeler**  
**Analysis Date:** March 2, 2026  
**Scenario:** S3 Progressive Subsidy (Bass Diffusion Model)

## Quick Start

1. **Read the full analysis**: [`der_load_shedding_analysis.md`](./der_load_shedding_analysis.md)
2. **Run the Python script**: `python3 load_shedding_mitigation_analysis.py`
3. **View summary data**: [`projections_summary.csv`](./projections_summary.csv)
4. **Explore detailed results**: [`projections_detailed.json`](./projections_detailed.json)

## Key Findings Summary

### 🔴 Critical Insight: Temporal Mismatch Dominates

**The potential of DER to mitigate load shedding is NOT about total installed capacity—it's about effective capacity during load shedding hours with islanding capability.**

- **Morning load shedding (6-9am)**: ~30% solar CF → moderate overlap
- **Evening load shedding (5-9pm)**: ~12.5% solar CF → SEVERE mismatch
- **Without storage**: DER provides minimal evening relief
- **With storage**: Evening capacity increases by 4× (72 MW → 292 MW by 2030)

### 📊 By the Numbers (2030 Projection)

| Metric | Without Storage | With Storage | Change |
|--------|-----------------|--------------|--------|
| **Evening effective capacity** | 72 MW | 292 MW | +306% |
| **Stage 4 evening coverage** | 12% | 49% | +37 pp |
| **Households that can island** | 0 | 75,064 (10.8%) | — |

### 🏘️ Equity Concerns

- Only **10.8%** of households can island during load shedding
- **68%** of islanding-capable households are high-income
- Low-income households: **3.8%** islanding capability
- **Risk**: Two-tier electricity system exacerbates inequality

### 🎯 Policy Recommendations

1. **Subsidize battery storage** alongside solar PV
2. **Mandate islanding-capable inverters** for new installations
3. **Means-tested subsidies**: 80% for low-income, 40% for middle-income
4. **Community battery storage** for low-income areas
5. **Monitor revenue erosion** to prevent utility death spiral

## Files in This Analysis

- **`der_load_shedding_analysis.md`**: Comprehensive 13,000-word analysis with methodology, results, policy implications
- **`load_shedding_mitigation_analysis.py`**: Python script for calculating effective DER capacity during load shedding
- **`projections_summary.csv`**: Tabular results for easy import into LEAP or Excel
- **`projections_detailed.json`**: Granular results by year, income group, and load shedding stage

## Methodology Highlights

1. **Eskom load shedding characterization**: Stages 1-8, typical schedules, Cape Town's 15% share
2. **Temporal overlap analysis**: Hourly solar CF vs. load shedding schedules
3. **Battery storage modeling**: 50% penetration, 45% round-trip utilization
4. **Household resilience**: Islanding capability by income group
5. **System-level impact**: Coverage % of Cape Town's load shedding burden

## Limitations & Future Work

### Completed in This Analysis
- ✅ Temporal mismatch quantification
- ✅ Storage impact modeling
- ✅ Household resilience by income group
- ✅ System-level coverage calculations
- ✅ Policy implications

### Not Yet Completed (Future Work)
- ⏳ **Part 2: Revenue Erosion Analysis** (mentioned in main report)
  - Calculate annual revenue loss from DER adoption
  - Model tariff increases for revenue neutrality
  - Analyze cross-subsidization erosion
  - Compare with international case studies (Australia, California, Hawaii)
- ⏳ Empirical validation using actual 2022-2024 load shedding data
- ⏳ LEAP model integration
- ⏳ Spatial analysis by Cape Town area
- ⏳ Commercial/industrial DER analysis

## Citation

```bibtex
@techreport{esm01_capetown_der_2026,
  title={Cape Town DER Potential to Mitigate Load Shedding: A Systems Analysis},
  author={ESM-01 Energy System Modeler},
  institution={Cape Town DER-LEAP Project},
  year={2026},
  month={March},
  note={S3 Progressive Subsidy Scenario, Bass Diffusion Model}
}
```

## Contact & Questions

- **GitHub Repository**: https://github.com/zl396/Cape-Town-DER-LEAP
- **Related Reports**:
  - Energy Modeling Team Final Report (2026)
  - Individual Policy Report: Zhenghao Lin (Spring 2026)

---

**Last Updated:** March 2, 2026  
**Analysis Status:** Part 1 Complete (Load Shedding Mitigation) | Part 2 Pending (Revenue Erosion)
