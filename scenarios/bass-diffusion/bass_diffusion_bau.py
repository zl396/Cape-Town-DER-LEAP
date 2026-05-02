#!/usr/bin/env python3
"""
Bass Diffusion Model: BAU (Business-As-Usual) Scenario
Cape Town DER-LEAP Project

Models SHS adoption under no-subsidy conditions using corrected data from
Biz's Mask2Former satellite detection pipeline (combined_02072026.parquet).

Bass Model (discrete):
    y_t = (m - Y_{t-1}) * [p + q * (Y_{t-1} / m)]
    Y_t = Y_{t-1} + y_t

Data Source (v3 — corrected):
    - Income groups: LifeLine=Low, Domestic=Mid, HomeUser=High (tariff-based)
    - Adoption rates: Biz's pipeline, 2022-2023 only (>98% coverage)
    - System sizes: Mean from Watt field (shs_area_m2 * 400/1.7, fallback total_capacity_va)
    - Household counts: Sales Summaries .xlsm, SUMMATED SALES sheet (2022/23)

Changes from old model:
    - Income mapping: was Postpaid=HI/Prepaid=MI → now HomeUser=HI/Domestic=MI/LifeLine=LI
    - HH counts: HI 158k→309k, MI 168k→150k, LI 307k→173k
    - System sizes: 8/5/3 kW → 4.91/3.66/2.84 kW (mean)
    - Calibration: was 2020-2023 (unreliable) → now 2022-2023 only
    - BAU saturation: was 30/20/0% → now 25/15/3% (data-driven)
    - Low-income: was 0% → now 0.64% baseline with 3% ceiling

Usage:
    python3 bass_diffusion_bau.py

Output:
    - bau_bass_diffusion_results.csv
    - bau_adoption_curves.png
    - bau_total_capacity.png
"""

import numpy as np
import csv
import os

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("WARNING: matplotlib not installed. Plots will be skipped.")

# ============================================================================
# CONFIGURATION — Corrected from Biz's Mask2Former pipeline
# ============================================================================

BASE_YEAR = 2022
CALIBRATION_END = 2023
PROJECTION_START = 2024
PROJECTION_END = 2050
LEAP_BASE_YEAR = 2018  # LEAP model starts here

# Household counts (2022/23 fiscal year, Sales Summaries)
# Source: analysis/income_group_shs_data.md Section 3
HH_COUNTS_2023 = {
    'high': 309_402,     # HomeUser (prepaid + credit, incl AMI)
    'middle': 150_534,   # Domestic (all sub-types)
    'low': 172_697,      # LifeLine 1&2 (all sub-types)
}

HH_GROWTH_RATE = 0.013  # 1.3% CAGR from IRP

# Average SHS system size (kW) — MEAN from actual data
# Source: analysis/income_group_shs_data.md Section 5
AVG_SYSTEM_SIZE = {
    'high': 4.91,    # Mean from Watt field, HomeUser accounts
    'middle': 3.66,  # Mean from Watt field, Domestic accounts
    'low': 2.84,     # Mean from Watt field, LifeLine accounts
}

# Historical adoption rates (2022-2023, reliable years only)
# Source: analysis/income_group_shs_data.md Section 4c
# 2020-2021 excluded: 58-67% prepaid accounts unmapped (trfname=NULL)
HISTORICAL_ADOPTION = {
    'high': {
        2022: 0.0484,   # 7,685 SHS / ~158k mapped HH (HomeUser)
        2023: 0.0729,   # 13,754 SHS / ~189k mapped HH
    },
    'middle': {
        2022: 0.0218,   # 3,507 SHS / ~161k mapped HH (Domestic)
        2023: 0.0328,   # 5,354 SHS / ~163k mapped HH
    },
    'low': {
        2022: 0.0051,   # 466 SHS / ~91k mapped HH (LifeLine)
        2023: 0.0064,   # 613 SHS / ~96k mapped HH
    },
}

# BAU saturation (m) — no-subsidy ceiling
# Derived from structural analysis: affordability, property ownership,
# roof suitability, load shedding motivation (see analysis session 2026-03-16)
BAU_PARAMS = {
    'high':   {'m': 0.25, 'q': 0.38},   # 25% — affluent, self-funded
    'middle': {'m': 0.15, 'q': 0.30},   # 15% — cost barrier, needs financing
    'low':    {'m': 0.03, 'q': 0.19},   # 3%  — minimal without subsidy
}

# Literature-based q values for solar PV adoption
# Sources: Batista da Silva et al., Schilling et al. 2009
LITERATURE_Q = {'high': 0.38, 'middle': 0.30, 'low': 0.19}

# SSEG historical capacity (MW) from City of Cape Town records
SSEG_HIST = {2018: 19, 2019: 31, 2020: 50, 2021: 73, 2022: 99, 2023: 121}
SSEG_CAPACITY_FACTOR = 0.196  # SOEC 2021
COMMERCIAL_MULTIPLIER = 1.25  # Residential + ~25% commercial

# Estimated 2018 adoption rates (smooth backfill anchors)
# Derived from exponential interpolation to match 2022 data
# HI: ~0.5% (early adopters pre-load-shedding), MI: ~0.1%, LI: ~0%
ADOPTION_2018 = {'high': 0.005, 'middle': 0.001, 'low': 0.0}


# ============================================================================
# SMOOTH BACKFILL: 2018-2022
# ============================================================================

def exponential_backfill(y_start, y_end, year_start, year_end):
    """
    Exponential interpolation from y_start (at year_start) to y_end (at year_end).
    Returns dict {year: value} for each integer year in [year_start, year_end].
    """
    n = year_end - year_start
    if n <= 0 or y_start <= 0:
        # Linear if start is zero
        result = {}
        for y in range(year_start, year_end + 1):
            t = (y - year_start) / n if n > 0 else 0
            result[y] = y_start + (y_end - y_start) * t
            result[y] = max(result[y], 0)
        return result
    # Exponential: y(t) = y_start * (y_end/y_start)^(t/n)
    ratio = y_end / y_start
    result = {}
    for y in range(year_start, year_end + 1):
        t = y - year_start
        result[y] = y_start * (ratio ** (t / n))
    return result


# ============================================================================
# BASS DIFFUSION MODEL
# ============================================================================

def bass_forward(m, p, q, Y0, n_years):
    """Forward simulate Bass model from initial adoption Y0."""
    Y = [Y0]
    for _ in range(n_years):
        Y_prev = Y[-1]
        if Y_prev >= m:
            Y.append(m)
            continue
        y_new = (m - Y_prev) * (p + q * (Y_prev / m))
        Y.append(min(Y_prev + y_new, m))
    return Y


def calibrate_p(m, q, Y_2022, Y_2023):
    """
    Calibrate innovation coefficient p from two consecutive adoption rates.

    From Bass equation:
        Y_2023 - Y_2022 = (m - Y_2022) * (p + q * Y_2022 / m)
    Solving for p:
        p = (Y_2023 - Y_2022) / (m - Y_2022) - q * Y_2022 / m
    """
    y_new = Y_2023 - Y_2022
    denom = m - Y_2022
    if denom <= 0:
        return 0.001
    p = y_new / denom - q * Y_2022 / m
    return max(p, 0.001)


# ============================================================================
# MAIN
# ============================================================================

def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 70)
    print("Bass Diffusion Model: BAU (Business-As-Usual) Scenario")
    print("Cape Town DER-LEAP Project — Corrected Data (v3)")
    print("=" * 70)

    # ---- Step 1: Calibrate Bass parameters per group ----
    print("\n--- Step 1: Calibrating Bass Parameters ---")
    print("Data: Biz's Mask2Former pipeline, 2022-2023 (>98% coverage)")
    print("Method: Fix q from literature, calibrate p from 2-point slope\n")

    params = {}
    for group in ['high', 'middle', 'low']:
        m = BAU_PARAMS[group]['m']
        q = BAU_PARAMS[group]['q']
        Y22 = HISTORICAL_ADOPTION[group][2022]
        Y23 = HISTORICAL_ADOPTION[group][2023]
        p = calibrate_p(m, q, Y22, Y23)

        params[group] = {'p': p, 'q': q, 'm': m}
        print(f"  [{group}] p={p:.6f}, q={q:.2f}, m={m*100:.0f}%")
        print(f"          Adoption: {Y22*100:.2f}% (2022) → {Y23*100:.2f}% (2023)")

    # ---- Step 2: Project adoption curves (2024-2050) + backfill (2018-2022) ----
    print("\n--- Step 2: Projecting Adoption Curves (2018-2050) ---")

    years = list(range(PROJECTION_START, PROJECTION_END + 1))
    n = len(years)  # 27 years

    projections = {}
    for group in ['high', 'middle', 'low']:
        Y0 = HISTORICAL_ADOPTION[group][2023]
        traj = bass_forward(
            params[group]['m'], params[group]['p'], params[group]['q'],
            Y0, n
        )
        # Build year->adoption dict including historical
        proj = {}
        # Smooth backfill 2018-2022
        backfill = exponential_backfill(
            ADOPTION_2018[group],
            HISTORICAL_ADOPTION[group][2022],
            LEAP_BASE_YEAR, 2022
        )
        proj.update(backfill)
        # Historical calibration points
        for y, v in HISTORICAL_ADOPTION[group].items():
            proj[y] = v
        # Bass forward projection
        for i, y in enumerate(years):
            proj[y] = traj[i + 1]  # traj[0] = Y0 = 2023
        proj[2023] = Y0
        projections[group] = proj

        for milestone in [2030, 2040, 2050]:
            print(f"  [{group}] {milestone}: {proj[milestone]*100:.2f}%")

    # ---- Step 3: Household counts ----
    print("\n--- Step 3: Household Count Projections ---")
    hh_projected = {}
    for group in ['high', 'middle', 'low']:
        hh_projected[group] = {}
        base = HH_COUNTS_2023[group]
        for y in range(LEAP_BASE_YEAR, PROJECTION_END + 1):
            hh_projected[group][y] = base * (HH_GROWTH_RATE + 1) ** (y - 2023)

    total_2050 = sum(hh_projected[g][2050] for g in ['high', 'middle', 'low'])
    print(f"  2050 total HH: {total_2050:,.0f}")

    # ---- Step 4: Capacity summary ----
    print("\n--- Step 4: BAU Capacity Summary ---")
    for milestone in [2025, 2030, 2040, 2050]:
        total_cap = 0
        for group in ['high', 'middle', 'low']:
            adoption = projections[group][milestone]
            hh = hh_projected[group][milestone]
            cap = adoption * hh * AVG_SYSTEM_SIZE[group] / 1000
            total_cap += cap
        sseg_total = total_cap * COMMERCIAL_MULTIPLIER
        print(f"  {milestone}: Residential={total_cap:.0f} MW, "
              f"Total SSEG={sseg_total:.0f} MW")

    # ---- Step 5: Generate CSV ----
    print("\n--- Step 5: Generating Outputs ---")
    csv_path = os.path.join(output_dir, 'bau_bass_diffusion_results.csv')

    all_years = sorted(set(
        list(range(LEAP_BASE_YEAR, PROJECTION_END + 1))
    ))

    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Year',
            'HI_Adoption_%', 'HI_HH_with_SHS', 'HI_Capacity_MW',
            'MI_Adoption_%', 'MI_HH_with_SHS', 'MI_Capacity_MW',
            'LI_Adoption_%', 'LI_HH_with_SHS', 'LI_Capacity_MW',
            'Total_HH_with_SHS', 'Total_Residential_Capacity_MW',
            'Total_SSEG_Capacity_MW',
        ])

        for y in all_years:
            row = [y]
            total_hh_shs = 0
            total_cap = 0

            for group in ['high', 'middle', 'low']:
                adoption = projections[group].get(y, 0)
                hh = hh_projected[group].get(y, 0)
                hh_shs = adoption * hh
                cap = hh_shs * AVG_SYSTEM_SIZE[group] / 1000

                row.extend([
                    f"{adoption * 100:.4f}",
                    f"{hh_shs:.0f}",
                    f"{cap:.2f}",
                ])
                total_hh_shs += hh_shs
                total_cap += cap

            sseg_total = total_cap * COMMERCIAL_MULTIPLIER
            row.extend([
                f"{total_hh_shs:.0f}",
                f"{total_cap:.2f}",
                f"{sseg_total:.2f}",
            ])
            writer.writerow(row)

    print(f"  CSV: {csv_path}")

    # ---- Step 6: Generate plots ----
    if HAS_MATPLOTLIB:
        plot_years = list(range(LEAP_BASE_YEAR, PROJECTION_END + 1))
        colors = {'high': '#2196F3', 'middle': '#FF9800', 'low': '#4CAF50'}
        labels = {'high': 'High-Income (HomeUser)', 'middle': 'Mid-Income (Domestic)', 'low': 'Low-Income (LifeLine)'}

        # Plot 1: Adoption curves
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('BAU: Bass Diffusion SHS Adoption Curves (Corrected Data)', fontsize=14)

        for idx, group in enumerate(['high', 'middle', 'low']):
            ax = axes[idx]
            adoption_pct = [projections[group].get(y, 0) * 100 for y in plot_years]
            ax.plot(plot_years, adoption_pct, color=colors[group], linewidth=2)
            ax.axhline(y=BAU_PARAMS[group]['m'] * 100, color='gray', linestyle='--',
                       alpha=0.5, label=f"Saturation ({BAU_PARAMS[group]['m']*100:.0f}%)")
            ax.set_title(labels[group])
            ax.set_xlabel('Year')
            ax.set_ylabel('SHS Adoption Rate (%)')
            ax.legend(fontsize=9)
            ax.set_xlim(LEAP_BASE_YEAR, 2050)
            ax.set_ylim(0, BAU_PARAMS[group]['m'] * 100 * 1.15)
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        path1 = os.path.join(output_dir, 'bau_adoption_curves.png')
        plt.savefig(path1, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Plot: {path1}")

        # Plot 2: Stacked capacity
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.suptitle('BAU: Total Residential SHS Capacity (Corrected Data)', fontsize=14)

        cap_by_group = {g: [] for g in ['high', 'middle', 'low']}
        total_cap_list = []
        for y in plot_years:
            tc = 0
            for group in ['high', 'middle', 'low']:
                adoption = projections[group].get(y, 0)
                hh = hh_projected[group].get(y, 0)
                cap = adoption * hh * AVG_SYSTEM_SIZE[group] / 1000
                cap_by_group[group].append(cap)
                tc += cap
            total_cap_list.append(tc)

        ax.stackplot(plot_years,
                     cap_by_group['low'], cap_by_group['middle'], cap_by_group['high'],
                     labels=['Low-Income', 'Mid-Income', 'High-Income'],
                     colors=['#4CAF50', '#FF9800', '#2196F3'], alpha=0.7)
        ax.plot(plot_years, total_cap_list, 'k-', linewidth=1.5, label='Total')
        ax.set_xlabel('Year')
        ax.set_ylabel('SHS Capacity (MW)')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        path2 = os.path.join(output_dir, 'bau_total_capacity.png')
        plt.savefig(path2, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Plot: {path2}")

    # ---- Print LEAP Interp() expressions ----
    print("\n" + "=" * 70)
    print("LEAP Interp() EXPRESSIONS — BAU SCENARIO")
    print("=" * 70)

    milestone_years = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2035, 2040, 2045, 2050]

    for group in ['high', 'middle', 'low']:
        label = {'high': 'High-Income', 'middle': 'Mid-Income', 'low': 'Low-Income'}[group]
        parts = []
        for y in milestone_years:
            rate = projections[group][y] * 100
            parts.append(f"{y}, {rate:.2f}")
        interp = "Interp(" + ", ".join(parts) + ")"
        print(f"\n  {label} → Grid and SHS:")
        print(f"  {interp}")
        print(f"  {label} → Grid Only: Remainder(100)")

    # SSEG Supply side
    print(f"\n  SSEG Total Capacity (MW):")
    parts = []
    for y in milestone_years:
        total_cap = 0
        for group in ['high', 'middle', 'low']:
            adoption = projections[group][y]
            hh = hh_projected[group][y]
            cap = adoption * hh * AVG_SYSTEM_SIZE[group] / 1000
            total_cap += cap
        sseg = total_cap * COMMERCIAL_MULTIPLIER
        parts.append(f"{y}, {sseg:.0f}")
    print(f"  Interp({', '.join(parts)})")

    print("\n" + "=" * 70)
    print("PARAMETER SUMMARY")
    print("=" * 70)
    print(f"{'Group':<10} {'p':>10} {'q':>6} {'m':>6} {'Y0 (2023)':>10} {'Sys kW':>8}")
    print("-" * 52)
    for group in ['high', 'middle', 'low']:
        Y0 = HISTORICAL_ADOPTION[group][2023]
        print(f"{group:<10} {params[group]['p']:>10.6f} {params[group]['q']:>6.2f} "
              f"{params[group]['m']*100:>5.0f}% {Y0*100:>9.2f}% {AVG_SYSTEM_SIZE[group]:>7.2f}")

    print("\n" + "=" * 70)
    print("DONE. Check output files in:", output_dir)
    print("=" * 70)

    return projections, params


if __name__ == '__main__':
    main()
