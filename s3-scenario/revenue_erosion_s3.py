#!/usr/bin/env python3
"""
Revenue Erosion Calculator for S3 Progressive Subsidy Scenario
Cape Town DER-LEAP Project

Calculates the revenue impact on City of Cape Town from SHS adoption under
the S3 progressive subsidy scenario, using the avoided generation method:

    Revenue Erosion = Avoided Grid Energy (kWh) × Tariff Rate (R/kWh)

Data sources:
    - s3_bass_diffusion_results.csv: SHS adoption projections (Bass model)
    - Yoder (2025) Ch. 3: Grid consumption reduction (~20-22%), revenue validation
    - Energy Modeling Team Final Report: HH energy intensity, tariffs (Tables 2, 8)

Validation:
    Yoder (2025) found 2023 revenue loss was 0.2% of total residential sales (~R291K).
    This calculator cross-validates against that benchmark.

Usage:
    python3 revenue_erosion_s3.py

Output:
    - s3_revenue_erosion_results.csv
    - s3_revenue_erosion.png
    - Console output with key findings
"""

import csv
import os
import numpy as np

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("WARNING: matplotlib not installed. Plots will be skipped.")

# ============================================================================
# CONFIGURATION
# ============================================================================

# Period
START_YEAR = 2020
END_YEAR = 2050

# Tariff escalation rate (10% annual, per user decision)
TARIFF_ESCALATION = 0.10

# Base year for tariffs
TARIFF_BASE_YEAR = 2024

# Cape Town 2024 electricity tariffs (R/kWh)
# Source: City of Cape Town approved tariffs, Energy Modeling Team Report Table 2
# LI = Lifeline tariff, MI = Domestic tariff, HI = Home User tariff
# Using weighted average across blocks (Block 1: 0-600 kWh, Block 2: 600+ kWh)
TARIFF_2024 = {
    'high': 3.50,       # Home User avg (R2.99 Block 1 + R4.13 Block 2) ≈ R3.50
    'middle': 3.50,     # Domestic avg (R3.40 Block 1 + R4.13 Block 2) ≈ R3.50
    'low': 2.06,        # Lifeline (R2.06 flat rate)
}

# Grid consumption reduction per SHS household (kWh/HH/year)
# Source: Energy Modeling Team Final Report, Table 8
# Verified by Yoder (2025): ~20-22% grid reduction for SHS households
GRID_REDUCTION_KWH = {
    'high': 1041,       # 6,533 Grid Only - 5,492 Grid+SHS = 1,041 kWh (16%)
    'middle': 1326,     # 6,347 Grid Only - 5,020 Grid+SHS = 1,326 kWh (21%)
    'low': 584,         # 3,887 Grid Only - 3,303 Grid+SHS = 584 kWh (15%)
}

# Average total household consumption (kWh/year) for % calculations
HH_CONSUMPTION_KWH = {
    'high': 6533,
    'middle': 6347,
    'low': 3887,
}

# Household growth rate (1.3% CAGR)
HH_GROWTH_RATE = 0.013

# Household counts (2022/23 baseline, Sales Summaries .xlsm)
# Income mapping: HomeUser=High, Domestic=Mid, LifeLine=Low
# Source: analysis/income_group_shs_data.md Section 3
HH_COUNTS_2023 = {
    'high': 309_402,     # HomeUser tariff
    'middle': 150_534,   # Domestic tariff
    'low': 172_697,      # LifeLine tariff
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def load_adoption_data(csv_path):
    """Load adoption data from s3_bass_diffusion_results.csv."""
    data = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = int(row['Year'])
            data[year] = {
                'high': {
                    'adoption_pct': float(row['HI_Adoption_%']) / 100,
                    'hh_with_shs': float(row['HI_HH_with_SHS']),
                },
                'middle': {
                    'adoption_pct': float(row['MI_Adoption_%']) / 100,
                    'hh_with_shs': float(row['MI_HH_with_SHS']),
                },
                'low': {
                    'adoption_pct': float(row['LI_Adoption_%']) / 100,
                    'hh_with_shs': float(row['LI_HH_with_SHS']),
                },
                'total_hh_shs': float(row['Total_HH_with_SHS']),
                'total_capacity_mw': float(row['Total_Residential_Capacity_MW']),
            }
    return data


def get_tariff(group, year):
    """Get tariff rate for a given income group and year."""
    base = TARIFF_2024[group]
    years_from_base = year - TARIFF_BASE_YEAR
    if years_from_base <= 0:
        # For years before 2024, deflate backwards
        return base / ((1 + TARIFF_ESCALATION) ** abs(years_from_base))
    return base * ((1 + TARIFF_ESCALATION) ** years_from_base)


def get_total_hh(group, year):
    """Get total household count for a given income group and year."""
    base = HH_COUNTS_2023[group]
    years_from_base = year - 2023
    return base * ((1 + HH_GROWTH_RATE) ** years_from_base)


def get_total_residential_revenue(year):
    """
    Estimate total residential electricity revenue for a given year.
    Total Revenue = Σ (Total HH × Avg Consumption × Tariff) for each group.
    """
    total = 0
    for group in ['high', 'middle', 'low']:
        hh = get_total_hh(group, year)
        consumption = HH_CONSUMPTION_KWH[group]
        tariff = get_tariff(group, year)
        total += hh * consumption * tariff
    return total


# ============================================================================
# MAIN CALCULATION
# ============================================================================

def calculate_revenue_erosion(adoption_data):
    """
    Calculate year-by-year revenue erosion from SHS adoption.

    Returns list of dicts with annual results.
    """
    results = []

    for year in sorted(adoption_data.keys()):
        if year < START_YEAR or year > END_YEAR:
            continue

        year_data = adoption_data[year]
        year_result = {'year': year}

        total_avoided_kwh = 0
        total_revenue_loss = 0

        for group in ['high', 'middle', 'low']:
            hh_shs = year_data[group]['hh_with_shs']
            adoption = year_data[group]['adoption_pct']
            tariff = get_tariff(group, year)

            # Avoided energy = HH with SHS × grid reduction per HH
            avoided_kwh = hh_shs * GRID_REDUCTION_KWH[group]
            avoided_mwh = avoided_kwh / 1000
            avoided_gwh = avoided_kwh / 1e6

            # Revenue loss = avoided energy × tariff
            revenue_loss_r = avoided_kwh * tariff
            revenue_loss_m = revenue_loss_r / 1e6  # millions of Rand

            year_result[f'{group}_hh_shs'] = hh_shs
            year_result[f'{group}_adoption_pct'] = adoption * 100
            year_result[f'{group}_avoided_gwh'] = avoided_gwh
            year_result[f'{group}_tariff_r_kwh'] = tariff
            year_result[f'{group}_revenue_loss_m'] = revenue_loss_m

            total_avoided_kwh += avoided_kwh
            total_revenue_loss += revenue_loss_r

        # Total residential revenue for context
        total_res_revenue = get_total_residential_revenue(year)

        year_result['total_avoided_gwh'] = total_avoided_kwh / 1e6
        year_result['total_revenue_loss_m'] = total_revenue_loss / 1e6
        year_result['total_residential_revenue_m'] = total_res_revenue / 1e6
        year_result['pct_of_residential_revenue'] = (
            (total_revenue_loss / total_res_revenue * 100) if total_res_revenue > 0 else 0
        )

        results.append(year_result)

    return results


def write_results_csv(results, output_path):
    """Write revenue erosion results to CSV."""
    fieldnames = [
        'year',
        'high_hh_shs', 'high_adoption_pct', 'high_avoided_gwh',
        'high_tariff_r_kwh', 'high_revenue_loss_m',
        'middle_hh_shs', 'middle_adoption_pct', 'middle_avoided_gwh',
        'middle_tariff_r_kwh', 'middle_revenue_loss_m',
        'low_hh_shs', 'low_adoption_pct', 'low_avoided_gwh',
        'low_tariff_r_kwh', 'low_revenue_loss_m',
        'total_avoided_gwh', 'total_revenue_loss_m',
        'total_residential_revenue_m', 'pct_of_residential_revenue',
    ]

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            # Round numeric values
            formatted = {}
            for k, v in row.items():
                if isinstance(v, float):
                    formatted[k] = f"{v:.4f}"
                else:
                    formatted[k] = v
            writer.writerow(formatted)

    print(f"CSV written to: {output_path}")


def generate_plots(results, output_dir):
    """Generate revenue erosion visualizations."""
    if not HAS_MATPLOTLIB:
        print("Skipping plots (matplotlib not installed)")
        return

    years = [r['year'] for r in results]

    # --- Plot 1: Revenue Erosion Over Time (2-panel) ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    fig.suptitle('S3 Progressive Subsidy: Revenue Erosion from SHS Adoption',
                 fontsize=14, fontweight='bold')

    # Panel 1: Revenue loss by income group (stacked area)
    hi_loss = [r['high_revenue_loss_m'] for r in results]
    mi_loss = [r['middle_revenue_loss_m'] for r in results]
    li_loss = [r['low_revenue_loss_m'] for r in results]
    total_loss = [r['total_revenue_loss_m'] for r in results]

    ax1.stackplot(years, li_loss, mi_loss, hi_loss,
                  labels=['Low-Income', 'Middle-Income', 'High-Income'],
                  colors=['#4CAF50', '#FF9800', '#2196F3'], alpha=0.7)
    ax1.plot(years, total_loss, 'k-', linewidth=1.5, label='Total')
    ax1.set_ylabel('Revenue Loss (R million)')
    ax1.set_title('Annual Revenue Erosion by Income Group')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    # Panel 2: % of total residential revenue
    pct_loss = [r['pct_of_residential_revenue'] for r in results]
    ax2.plot(years, pct_loss, 'r-', linewidth=2, label='% of Residential Revenue')
    ax2.fill_between(years, pct_loss, alpha=0.2, color='red')

    # Add Yoder benchmark
    yoder_2023_idx = next((i for i, r in enumerate(results) if r['year'] == 2023), None)
    if yoder_2023_idx is not None:
        ax2.plot(2023, 0.2, 'ko', markersize=10, label='Yoder (2025) observed: 0.2%')
        ax2.annotate('Yoder benchmark\n(0.2% in 2023)',
                     xy=(2023, 0.2), xytext=(2028, 0.5),
                     arrowprops=dict(arrowstyle='->', color='black'),
                     fontsize=9)

    ax2.set_xlabel('Year')
    ax2.set_ylabel('Revenue Loss (% of residential sales)')
    ax2.set_title('Revenue Erosion as Percentage of Total Residential Revenue')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    path1 = os.path.join(output_dir, 's3_revenue_erosion.png')
    plt.savefig(path1, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Plot saved: {path1}")

    # --- Plot 2: Avoided Generation ---
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.suptitle('S3 Progressive Subsidy: Avoided Grid Generation from SHS',
                 fontsize=14, fontweight='bold')

    hi_gwh = [r['high_avoided_gwh'] for r in results]
    mi_gwh = [r['middle_avoided_gwh'] for r in results]
    li_gwh = [r['low_avoided_gwh'] for r in results]
    total_gwh = [r['total_avoided_gwh'] for r in results]

    ax.stackplot(years, li_gwh, mi_gwh, hi_gwh,
                 labels=['Low-Income', 'Middle-Income', 'High-Income'],
                 colors=['#4CAF50', '#FF9800', '#2196F3'], alpha=0.7)
    ax.plot(years, total_gwh, 'k-', linewidth=1.5, label='Total')
    ax.set_xlabel('Year')
    ax.set_ylabel('Avoided Grid Energy (GWh)')
    ax.set_title('Electricity Sales Displaced by Residential SHS')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path2 = os.path.join(output_dir, 's3_avoided_generation.png')
    plt.savefig(path2, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Plot saved: {path2}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    csv_input = os.path.join(output_dir, 's3_bass_diffusion_results.csv')

    print("=" * 70)
    print("Revenue Erosion Calculator: S3 Progressive Subsidy Scenario")
    print("Cape Town DER-LEAP Project")
    print("=" * 70)

    # Load adoption data
    print(f"\nLoading adoption data from: {csv_input}")
    if not os.path.exists(csv_input):
        print("ERROR: s3_bass_diffusion_results.csv not found!")
        print("Run bass_diffusion_s3.py first to generate adoption projections.")
        return

    adoption_data = load_adoption_data(csv_input)
    print(f"Loaded {len(adoption_data)} years of data ({min(adoption_data)}–{max(adoption_data)})")

    # Calculate revenue erosion
    print("\n--- Calculating Revenue Erosion ---")
    print(f"Tariff escalation: {TARIFF_ESCALATION*100:.0f}% annual")
    print(f"Base tariffs (2024): HI=R{TARIFF_2024['high']:.2f}, "
          f"MI=R{TARIFF_2024['middle']:.2f}, LI=R{TARIFF_2024['low']:.2f}")

    results = calculate_revenue_erosion(adoption_data)

    # Print key results
    print("\n--- Key Results ---\n")
    print(f"{'Year':<6} {'Avoided GWh':>12} {'Rev Loss (Rm)':>14} "
          f"{'Total Rev (Rm)':>15} {'% of Revenue':>13}")
    print("-" * 62)

    for r in results:
        if r['year'] in [2020, 2023, 2025, 2030, 2035, 2040, 2045, 2050]:
            print(f"{r['year']:<6} {r['total_avoided_gwh']:>12.2f} "
                  f"{r['total_revenue_loss_m']:>14.2f} "
                  f"{r['total_residential_revenue_m']:>15.1f} "
                  f"{r['pct_of_residential_revenue']:>12.3f}%")

    # Yoder validation
    print("\n--- Yoder (2025) Validation ---")
    r2023 = next((r for r in results if r['year'] == 2023), None)
    if r2023:
        print(f"Our 2023 estimate: {r2023['pct_of_residential_revenue']:.3f}% "
              f"(R{r2023['total_revenue_loss_m']:.2f}m)")
        print(f"Yoder (2025) observed: 0.2% of total residential sales ($291K USD ≈ R5.4m)")
        ratio = r2023['pct_of_residential_revenue'] / 0.2 if 0.2 > 0 else 0
        if ratio > 2:
            print(f"  → Our estimate is {ratio:.1f}x Yoder's (% basis). Reasons:")
            print(f"    - Yoder uses ACTUAL billing data (captures partial-year adopters)")
            print(f"    - Our model assumes full-year grid reduction for all SHS HH")
            print(f"    - Grid reduction values (1,041/1,326/584 kWh) are theoretical")
            print(f"      estimates from Energy Modeling Team report, not measured")
            print(f"    - Actual grid reduction per HH may be ~25% of theoretical values")
            print(f"    - Consider using Yoder's regression coefficient (β₂≈-20%)")
            print(f"      × actual HH consumption to get more realistic estimates")
        elif ratio < 0.5:
            print(f"  → Our estimate is only {ratio:.1f}x Yoder's. Consider increasing "
                  f"grid reduction values.")
        else:
            print(f"  → Ratio: {ratio:.1f}x (within reasonable range)")

    # Income group breakdown for 2050
    print("\n--- 2050 Revenue Erosion Breakdown ---")
    r2050 = next((r for r in results if r['year'] == 2050), None)
    if r2050:
        for group in ['high', 'middle', 'low']:
            label = {'high': 'High-Income', 'middle': 'Middle-Income', 'low': 'Low-Income'}
            print(f"  {label[group]:<16} "
                  f"Avoided: {r2050[f'{group}_avoided_gwh']:.1f} GWh, "
                  f"Revenue Loss: R{r2050[f'{group}_revenue_loss_m']:.1f}m, "
                  f"Tariff: R{r2050[f'{group}_tariff_r_kwh']:.2f}/kWh")
        print(f"  {'TOTAL':<16} "
              f"Avoided: {r2050['total_avoided_gwh']:.1f} GWh, "
              f"Revenue Loss: R{r2050['total_revenue_loss_m']:.1f}m")
        print(f"  As % of residential revenue: {r2050['pct_of_residential_revenue']:.2f}%")

    # Write outputs
    print("\n--- Generating Outputs ---")
    csv_output = os.path.join(output_dir, 's3_revenue_erosion_results.csv')
    write_results_csv(results, csv_output)
    generate_plots(results, output_dir)

    print("\n" + "=" * 70)
    print("DONE. Revenue erosion analysis complete.")
    print("=" * 70)

    return results


if __name__ == '__main__':
    main()
