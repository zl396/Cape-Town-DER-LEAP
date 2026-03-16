# Cape Town DER-LEAP

Distributed Energy Resources (DER) modeling for Cape Town using LEAP (Low Emissions Analysis Platform). This project models solar home system (SHS) adoption across income groups and evaluates policy scenarios for equitable energy transition.

## Repository Structure

```
├── model/                  # LEAP model file and shared assumptions
├── s3-scenario/            # S3 Progressive Subsidy scenario
│   ├── bass_diffusion_s3.py        # Bass diffusion adoption model
│   ├── revenue_erosion_s3.py       # Municipal revenue impact model
│   ├── generate_excel.py           # Export assumptions to Excel for LEAP
│   └── LEAP_S3_implementation_guide.md
├── analysis/               # DER load shedding mitigation analysis
├── references/             # Background literature and reports
└── ai-agent-engineering/   # AI agent engineering principles
```

## Scenarios

| Scenario | Description |
|----------|-------------|
| **BAU** | Business-As-Usual baseline with current adoption trends |
| **S3** | Progressive Subsidy — income-scaled subsidies (largest for low-income, none for high-income) |

## Data Sources

- **SHS adoption (historical):** Yoder (2025) dissertation Ch. 3 — Mask2Former deep learning on aerial imagery (2020-2023)
- **Household counts:** City of Cape Town metering data via Energy Modeling Team Final Report
- **Income group classification:** Tariff categories (LifeLine / Domestic / HomeUser) from municipal billing data
- **LEAP model:** `capetown_07072025.leap`

## Key Methods

- **Bass diffusion model** for SHS adoption projections (calibrated to 2020-2023 aerial imagery data)
- **Revenue erosion analysis** for municipal financial impact of DER growth
- **LEAP integration** for long-term energy system planning (2024-2050)
