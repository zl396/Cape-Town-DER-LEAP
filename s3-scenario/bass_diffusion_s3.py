#!/usr/bin/env python3
"""
Bass Diffusion Model for S3 Progressive Subsidy Scenario
Cape Town DER-LEAP Project — Corrected Data (v3)

Models SHS adoption under progressive subsidy policy using corrected data from
Biz's Mask2Former satellite detection pipeline (combined_02072026.parquet).

Bass Model (discrete):
    y_t = (m - Y_{t-1}) * [p + q * (Y_{t-1} / m)]
    Y_t = Y_{t-1} + y_t

Data Source (v3 — corrected):
    - Income groups: LifeLine=Low, Domestic=Mid, HomeUser=High (tariff-based)
    - Adoption rates: Biz's pipeline, 2022-2023 only (>98% coverage)
    - System sizes: Mean from Watt field (4.91/3.66/2.84 kW)
    - Household counts: Sales Summaries .xlsm (2022/23)
    - Calibration: 2022-2023 only (2020-21 excluded: 58-67% unmapped prepaid)

Changes from old model (v2):
    - Income mapping: Postpaid=HI/Prepaid=MI → HomeUser=HI/Domestic=MI/LifeLine=LI
    - HH counts: HI 158k→309k, MI 168k→150k, LI 307k→173k
    - System sizes: 8/5/3 kW → 4.91/3.66/2.84 kW (mean)
    - S3 saturation: 30/25/15% (unchanged from v2 design)
    - BAU baseline: now 25/15/3% (was 30/20/0%)

Usage:
    python3 bass_diffusion_s3.py

Output:
    - s3_bass_diffusion_results.csv
    - s3_adoption_curves.png
    - s3_sensitivity_analysis.png
    - Console output with calibration results
"""

import numpy as np
import csv
import os

# Try importing optional dependencies
try:
    from scipy.optimize import curve_fit
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("WARNING: scipy not installed. Calibration will use default parameters.")
    print("Install with: pip3 install scipy")

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("WARNING: matplotlib not installed. Plots will be skipped.")
    print("Install with: pip3 install matplotlib")

# ============================================================================
# CONFIGURATION - Edit these values as needed
# ============================================================================

# Projection period
BASE_YEAR = 2022       # Reliable data starts 2022 (>98% tariff coverage)
CALIBRATION_END = 2023
PROJECTION_START = 2024
PROJECTION_END = 2050

# Household counts (2022/23 fiscal year, Sales Summaries .xlsm)
# Source: analysis/income_group_shs_data.md Section 3
# Income mapping: HomeUser=High, Domestic=Mid, LifeLine=Low
HH_COUNTS = {
    'high': {2022: 309_402, 2023: 309_402},    # HomeUser tariff
    'middle': {2022: 150_534, 2023: 150_534},   # Domestic tariff
    'low': {2022: 172_697, 2023: 172_697},       # LifeLine tariff
}

# Household growth rate for projections (1.3% CAGR from IRP)
HH_GROWTH_RATE = 0.013

# Average SHS system size per income group (kW) — MEAN from actual data
# Source: analysis/income_group_shs_data.md Section 5
# Derived from Watt field = shs_area_m2 * 400/1.7, fallback total_capacity_va
AVG_SYSTEM_SIZE = {'high': 4.91, 'middle': 3.66, 'low': 2.84}

# Total SSEG capacity (MW) - from LEAP model supply side (Table 16)
TOTAL_SSEG_CAPACITY_MW = {2018: 19, 2019: 31, 2020: 50, 2021: 73, 2022: 99, 2023: 121}

# Commercial SSEG multiplier (residential + ~25% commercial)
COMMERCIAL_MULTIPLIER = 1.25

# ============================================================================
# HISTORICAL ADOPTION DATA
# ============================================================================
# Source: Biz's Mask2Former pipeline (combined_02072026.parquet)
# Income mapping: HomeUser=High, Domestic=Mid, LifeLine=Low (tariff-based)
# Only 2022-2023 used for calibration (>98% tariff coverage)
# 2020-2021 excluded: 58-67% prepaid accounts have trfname=NULL
# See analysis/income_group_shs_data.md Section 4

HISTORICAL_ADOPTION = {
    'high': {
        2022: 0.0484,   # 7,685 SHS / HomeUser accounts
        2023: 0.0729,   # 13,754 SHS / HomeUser accounts
    },
    'middle': {
        2022: 0.0218,   # 3,507 SHS / Domestic accounts
        2023: 0.0328,   # 5,354 SHS / Domestic accounts
    },
    'low': {
        2022: 0.0051,   # 466 SHS / LifeLine accounts
        2023: 0.0064,   # 613 SHS / LifeLine accounts
    },
}

# ============================================================================
# S3 SCENARIO PARAMETERS - Progressive Subsidy
# ============================================================================
# S3 market saturation caps (m): policy-enhanced ceilings
# BAU baseline: High=25%, Mid=15%, Low=3%
# S3 subsidy lifts: High unchanged, Mid +10pp, Low +12pp
S3_PARAMS = {
    'high': {
        'm': 0.30,      # 30% saturation (BAU=25%, +5pp from organic growth)
        'p': None,       # Calibrated from data
        'q': None,       # From literature
        'Y0': None,      # From historical data (2023 value)
    },
    'middle': {
        'm': 0.25,       # 25% saturation (BAU=15%, moderate subsidy)
        'p': None,       # Calibrated then multiplied (1.5x)
        'q': None,       # From literature
        'Y0': None,      # From historical data
    },
    'low': {
        'm': 0.15,       # 15% saturation (BAU=3%, largest subsidy)
        'p': None,       # Calibrated then multiplied (2.5x)
        'q': None,       # From literature
        'Y0': None,      # From historical data (0.64% in 2023)
    },
}

# Policy multipliers for p and q relative to calibrated high-income values
# These reflect the progressive subsidy design:
# - Larger subsidies for lower income groups increase p (policy push)
# - Peer effects (q) vary by social network characteristics
POLICY_MULTIPLIERS = {
    'middle': {'p_mult': 1.5, 'q_mult': 0.8},
    'low': {'p_mult': 2.5, 'q_mult': 0.5},
}

# Default parameters if calibration is not possible
# These are literature-informed values for solar PV adoption:
# - p for solar PV typically ranges 0.001-0.03 (annual)
# - q for solar PV typically ranges 0.3-0.6 (annual)
# Sources: Batista da Silva et al. (PV using Bass model), Mejia 2024,
#          Schilling et al. 2009 (renewable energy S-curves)
DEFAULT_PARAMS = {
    'high': {'p': 0.008, 'q': 0.38},
    'middle': {'p': 0.012, 'q': 0.30},
    'low': {'p': 0.020, 'q': 0.19},
}

# Literature-based q values for solar PV adoption
# Used in hybrid calibration when data-only calibration yields q ≈ 0
# (common with few data points in early adoption phase)
LITERATURE_Q = {
    'high': 0.38,    # Strong peer effects in affluent neighborhoods
    'middle': 0.30,  # Moderate peer effects
    'low': 0.19,     # Weaker but non-zero peer effects (community programs)
}

# Calibration mode: 'data_only', 'hybrid', or 'default'
# - 'data_only': fit both p and q from data (may give q≈0 with few points)
# - 'hybrid': fix q from literature, calibrate p from data (RECOMMENDED)
# - 'default': use DEFAULT_PARAMS directly, no calibration
CALIBRATION_MODE = 'hybrid'


# ============================================================================
# BASS DIFFUSION MODEL
# ============================================================================

def bass_cumulative(t, p, q, m, Y0=0):
    """
    Compute cumulative Bass diffusion adoption over time (discrete).

    Parameters:
        t: array of time periods (integers, 0-indexed)
        p: innovation coefficient
        q: imitation coefficient
        m: market saturation (as fraction, e.g. 0.30 for 30%)
        Y0: initial cumulative adoption at t=0

    Returns:
        Array of cumulative adoption fractions at each time t
    """
    Y = np.zeros(len(t))
    Y[0] = Y0

    for i in range(1, len(t)):
        remaining = m - Y[i-1]
        if remaining <= 0:
            Y[i] = m
            continue
        new_adopters = remaining * (p + q * (Y[i-1] / m)) if m > 0 else 0
        new_adopters = max(0, min(new_adopters, remaining))
        Y[i] = Y[i-1] + new_adopters

    return Y


def bass_continuous(t, p, q, m, Y0=0):
    """
    Continuous-time Bass diffusion model (closed-form solution).
    Used for curve fitting.

    F(t) = m * [1 - e^(-(p+q)*t)] / [1 + (q/p) * e^(-(p+q)*t)]

    Parameters:
        t: time array (float)
        p: innovation coefficient
        q: imitation coefficient
        m: market saturation
        Y0: initial adoption (added as offset)

    Returns:
        Cumulative adoption at each time t
    """
    if p <= 0 or q <= 0 or m <= 0:
        return np.full_like(t, Y0, dtype=float)

    exp_term = np.exp(-(p + q) * t)
    F = m * (1 - exp_term) / (1 + (q / p) * exp_term)
    return np.maximum(F, Y0)


def bass_for_fitting(t, p, q):
    """Bass model wrapper for scipy curve_fit with fixed m and Y0."""
    return bass_continuous(t, p, q, _fit_m, _fit_Y0)


# ============================================================================
# CALIBRATION
# ============================================================================

def calibrate_bass(historical_data, m, group_name='', mode=None):
    """
    Calibrate Bass model p, q using historical adoption data.

    Supports three modes:
    - 'data_only': fit both p and q from data
    - 'hybrid': fix q from literature, calibrate only p from data
    - 'default': use DEFAULT_PARAMS directly

    Parameters:
        historical_data: dict {year: adoption_fraction}
        m: market saturation cap
        group_name: label for printing
        mode: calibration mode (defaults to CALIBRATION_MODE global)

    Returns:
        (p, q, r_squared, rmse)
    """
    global _fit_m, _fit_Y0

    if mode is None:
        mode = CALIBRATION_MODE

    years = sorted(historical_data.keys())
    values = np.array([historical_data[y] for y in years])
    t = np.array([y - years[0] for y in years], dtype=float)

    _fit_m = m
    _fit_Y0 = values[0]

    # Default mode: no calibration
    if mode == 'default':
        dp = DEFAULT_PARAMS.get(group_name, {'p': 0.01, 'q': 0.3})
        print(f"  [{group_name}] Using default: p={dp['p']:.6f}, q={dp['q']:.6f}")
        return dp['p'], dp['q'], None, None

    # With only 2 data points, use direct algebraic calibration
    if len(values) == 2:
        q_fixed = LITERATURE_Q.get(group_name, 0.30)
        Y0, Y1 = values[0], values[1]
        y_new = Y1 - Y0
        denom = m - Y0
        if denom > 0:
            p_calc = y_new / denom - q_fixed * Y0 / m
            p_calc = max(p_calc, 0.001)
        else:
            p_calc = 0.001
        print(f"  [{group_name}] 2-point calibrated: p={p_calc:.6f}, q={q_fixed:.6f} (fixed)")
        return p_calc, q_fixed, None, None

    if not HAS_SCIPY or len(values) < 3:
        dp = DEFAULT_PARAMS.get(group_name, {'p': 0.01, 'q': 0.3})
        print(f"  [{group_name}] Using default (insufficient data or no scipy)")
        return dp['p'], dp['q'], None, None

    # Check if all values are zero (can't calibrate)
    if np.all(values == 0):
        dp = DEFAULT_PARAMS.get(group_name, {'p': 0.01, 'q': 0.3})
        print(f"  [{group_name}] All zero adoption data, using default parameters")
        return dp['p'], dp['q'], None, None

    # Hybrid mode: fix q from literature, fit only p
    if mode == 'hybrid':
        q_fixed = LITERATURE_Q.get(group_name, 0.30)

        def bass_hybrid_fit(t, p):
            return bass_continuous(t, p, q_fixed, m, values[0])

        try:
            popt, _ = curve_fit(
                bass_hybrid_fit, t, values,
                p0=[0.01],
                bounds=([1e-6], [0.5]),
                maxfev=10000,
            )
            p_fit = popt[0]

            predicted = bass_continuous(t, p_fit, q_fixed, m, values[0])
            ss_res = np.sum((values - predicted) ** 2)
            ss_tot = np.sum((values - np.mean(values)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            rmse = np.sqrt(np.mean((values - predicted) ** 2))

            print(f"  [{group_name}] Hybrid calibrated: p={p_fit:.6f}, q={q_fixed:.6f} (fixed)")
            print(f"  [{group_name}] R²={r_squared:.4f}, RMSE={rmse:.6f}")
            return p_fit, q_fixed, r_squared, rmse

        except Exception as e:
            print(f"  [{group_name}] Hybrid calibration failed: {e}, using defaults")
            dp = DEFAULT_PARAMS.get(group_name, {'p': 0.01, 'q': 0.3})
            return dp['p'], dp['q'], None, None

    # Data-only mode: fit both p and q
    try:
        popt, pcov = curve_fit(
            bass_for_fitting, t, values,
            p0=[0.01, 0.3],
            bounds=([1e-6, 1e-6], [0.5, 2.0]),
            maxfev=10000,
        )
        p_fit, q_fit = popt

        predicted = bass_continuous(t, p_fit, q_fit, m, values[0])
        ss_res = np.sum((values - predicted) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        rmse = np.sqrt(np.mean((values - predicted) ** 2))

        # Warn if q is essentially zero
        if q_fit < 0.001:
            print(f"  [{group_name}] WARNING: q≈0 (no imitation effect detected).")
            print(f"  [{group_name}] This is common with few data points in early adoption.")
            print(f"  [{group_name}] Consider using CALIBRATION_MODE='hybrid' instead.")

        print(f"  [{group_name}] Data-only calibrated: p={p_fit:.6f}, q={q_fit:.6f}")
        print(f"  [{group_name}] R²={r_squared:.4f}, RMSE={rmse:.6f}")
        return p_fit, q_fit, r_squared, rmse

    except Exception as e:
        print(f"  [{group_name}] Calibration failed: {e}, using defaults")
        dp = DEFAULT_PARAMS.get(group_name, {'p': 0.01, 'q': 0.3})
        return dp['p'], dp['q'], None, None


# ============================================================================
# PROJECTION
# ============================================================================

def project_hh_counts(base_year_counts, growth_rate, start_year, end_year):
    """Project household counts forward using CAGR."""
    counts = {}
    base_year = max(base_year_counts.keys())
    base_count = base_year_counts[base_year]

    # Include historical data
    for y, c in base_year_counts.items():
        counts[y] = c

    # Project forward
    for y in range(base_year + 1, end_year + 1):
        years_forward = y - base_year
        counts[y] = base_count * (1 + growth_rate) ** years_forward

    return counts


def run_projection(p, q, m, Y0, start_year, end_year, calibration_start=None):
    """
    Run Bass diffusion projection.

    Parameters:
        p, q, m: Bass parameters
        Y0: initial adoption at start_year
        start_year, end_year: projection period
        calibration_start: if provided, include historical period

    Returns:
        dict {year: cumulative_adoption_fraction}
    """
    if calibration_start:
        n_years = end_year - calibration_start + 1
        t = np.arange(n_years)
        years = list(range(calibration_start, end_year + 1))
    else:
        n_years = end_year - start_year + 1
        t = np.arange(n_years)
        years = list(range(start_year, end_year + 1))

    adoption = bass_cumulative(t, p, q, m, Y0)
    return dict(zip(years, adoption))


def run_sensitivity(p_base, q_base, m, Y0, start_year, end_year, variation=0.30):
    """
    Run sensitivity analysis varying p and q by ±variation.

    Returns dict with keys: 'base', 'high_p', 'low_p', 'high_q', 'low_q',
    'high_both', 'low_both'
    """
    scenarios = {
        'base': (p_base, q_base),
        'high_p_high_q': (p_base * (1 + variation), q_base * (1 + variation)),
        'low_p_low_q': (p_base * (1 - variation), q_base * (1 - variation)),
        'high_p_low_q': (p_base * (1 + variation), q_base * (1 - variation)),
        'low_p_high_q': (p_base * (1 - variation), q_base * (1 + variation)),
    }

    results = {}
    for name, (p, q) in scenarios.items():
        results[name] = run_projection(p, q, m, Y0, start_year, end_year)

    return results


# ============================================================================
# OUTPUT
# ============================================================================

def generate_csv(results, hh_counts, output_path):
    """
    Generate CSV with year-by-year results for all income groups.

    Columns: Year, HI_adoption%, HI_HH_with_SHS, HI_capacity_MW,
             MI_adoption%, MI_HH_with_SHS, MI_capacity_MW,
             LI_adoption%, LI_HH_with_SHS, LI_capacity_MW,
             Total_HH_with_SHS, Total_capacity_MW
    """
    years = sorted(results['high'].keys())

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Year',
            'HI_Adoption_%', 'HI_HH_with_SHS', 'HI_Capacity_MW',
            'MI_Adoption_%', 'MI_HH_with_SHS', 'MI_Capacity_MW',
            'LI_Adoption_%', 'LI_HH_with_SHS', 'LI_Capacity_MW',
            'Total_HH_with_SHS', 'Total_Residential_Capacity_MW',
        ])

        for y in years:
            row = [y]
            total_hh = 0
            total_cap = 0

            for group in ['high', 'middle', 'low']:
                adoption = results[group].get(y, 0)
                hh = hh_counts[group].get(y, 0)
                hh_shs = adoption * hh
                cap = hh_shs * AVG_SYSTEM_SIZE[group] / 1000  # kW to MW

                row.extend([
                    f"{adoption * 100:.4f}",
                    f"{hh_shs:.0f}",
                    f"{cap:.2f}",
                ])
                total_hh += hh_shs
                total_cap += cap

            row.extend([f"{total_hh:.0f}", f"{total_cap:.2f}"])
            writer.writerow(row)

    print(f"\nCSV written to: {output_path}")


def generate_plots(results, sensitivity_results, hh_counts, output_dir):
    """Generate adoption curve and sensitivity analysis plots."""
    if not HAS_MATPLOTLIB:
        print("Skipping plots (matplotlib not installed)")
        return

    years = sorted(results['high'].keys())

    # --- Plot 1: Adoption Curves ---
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('S3 Progressive Subsidy: Bass Diffusion Adoption Curves', fontsize=14)

    colors = {'high': '#2196F3', 'middle': '#FF9800', 'low': '#4CAF50'}
    labels = {'high': 'High-Income', 'middle': 'Middle-Income', 'low': 'Low-Income'}
    saturation = {'high': 30, 'middle': 25, 'low': 15}

    for idx, group in enumerate(['high', 'middle', 'low']):
        ax = axes[idx]
        adoption_pct = [results[group].get(y, 0) * 100 for y in years]
        ax.plot(years, adoption_pct, color=colors[group], linewidth=2, label='Bass Model')
        ax.axhline(y=saturation[group], color='gray', linestyle='--', alpha=0.5,
                    label=f'Saturation ({saturation[group]}%)')
        ax.set_title(f'{labels[group]}')
        ax.set_xlabel('Year')
        ax.set_ylabel('SHS Adoption Rate (%)')
        ax.legend(fontsize=9)
        ax.set_xlim(BASE_YEAR, PROJECTION_END)
        ax.set_ylim(0, max(saturation[group] * 1.1, 5))
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path1 = os.path.join(output_dir, 's3_adoption_curves.png')
    plt.savefig(path1, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Plot saved: {path1}")

    # --- Plot 2: Total Capacity ---
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.suptitle('S3 Progressive Subsidy: Total Residential SHS Capacity', fontsize=14)

    total_cap = []
    cap_by_group = {g: [] for g in ['high', 'middle', 'low']}

    for y in years:
        tc = 0
        for group in ['high', 'middle', 'low']:
            adoption = results[group].get(y, 0)
            hh = hh_counts[group].get(y, 0)
            cap = adoption * hh * AVG_SYSTEM_SIZE[group] / 1000
            cap_by_group[group].append(cap)
            tc += cap
        total_cap.append(tc)

    ax.stackplot(years,
                 cap_by_group['low'], cap_by_group['middle'], cap_by_group['high'],
                 labels=['Low-Income', 'Middle-Income', 'High-Income'],
                 colors=['#4CAF50', '#FF9800', '#2196F3'], alpha=0.7)
    ax.plot(years, total_cap, 'k-', linewidth=1.5, label='Total')
    ax.set_xlabel('Year')
    ax.set_ylabel('SHS Capacity (MW)')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path2 = os.path.join(output_dir, 's3_total_capacity.png')
    plt.savefig(path2, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Plot saved: {path2}")

    # --- Plot 3: Sensitivity Analysis ---
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('S3 Sensitivity Analysis: ±30% Variation in p and q', fontsize=14)

    sens_labels = {
        'base': 'Baseline',
        'high_p_high_q': 'High p, High q (+30%)',
        'low_p_low_q': 'Low p, Low q (-30%)',
        'high_p_low_q': 'High p, Low q',
        'low_p_high_q': 'Low p, High q',
    }
    sens_styles = {
        'base': {'color': 'black', 'linewidth': 2, 'linestyle': '-'},
        'high_p_high_q': {'color': 'red', 'linewidth': 1.5, 'linestyle': '--'},
        'low_p_low_q': {'color': 'blue', 'linewidth': 1.5, 'linestyle': '--'},
        'high_p_low_q': {'color': 'orange', 'linewidth': 1, 'linestyle': ':'},
        'low_p_high_q': {'color': 'green', 'linewidth': 1, 'linestyle': ':'},
    }

    for idx, group in enumerate(['high', 'middle', 'low']):
        ax = axes[idx]
        for scenario_name, data in sensitivity_results[group].items():
            proj_years = sorted(data.keys())
            values = [data[y] * 100 for y in proj_years]
            style = sens_styles[scenario_name]
            ax.plot(proj_years, values, label=sens_labels[scenario_name], **style)

        ax.axhline(y=saturation[group], color='gray', linestyle='--', alpha=0.5)
        ax.set_title(f'{labels[group]}')
        ax.set_xlabel('Year')
        ax.set_ylabel('SHS Adoption Rate (%)')
        ax.legend(fontsize=7, loc='upper left')
        ax.set_xlim(PROJECTION_START, PROJECTION_END)
        ax.set_ylim(0, max(saturation[group] * 1.3, 5))
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path3 = os.path.join(output_dir, 's3_sensitivity_analysis.png')
    plt.savefig(path3, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Plot saved: {path3}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 70)
    print("Bass Diffusion Model: S3 Progressive Subsidy Scenario")
    print("Cape Town DER-LEAP Project")
    print("=" * 70)

    # ---- Step 1: Calibrate high-income Bass parameters ----
    print(f"\n--- Step 1: Calibrating High-Income Bass Parameters ---")
    print(f"Calibration mode: {CALIBRATION_MODE}")
    print("Using Yoder (2025) aerial imagery SHS adoption data (2020-2023)")
    print("Source: Mask2Former detection on aerial imagery (~3x more accurate than registration)\n")

    p_hi, q_hi, r2_hi, rmse_hi = calibrate_bass(
        HISTORICAL_ADOPTION['high'],
        m=S3_PARAMS['high']['m'],
        group_name='high'
    )

    # ---- Step 2: Derive middle and low-income parameters ----
    print("\n--- Step 2: Deriving Middle/Low-Income Parameters ---")
    print(f"Base (calibrated HI): p={p_hi:.6f}, q={q_hi:.6f}")
    print("Progressive subsidy: p increases, q adjusted for each income group\n")

    # Middle-income: moderate subsidy -> p increased, q from literature or scaled
    p_mi = p_hi * POLICY_MULTIPLIERS['middle']['p_mult']
    q_mi = LITERATURE_Q['middle'] if CALIBRATION_MODE == 'hybrid' else q_hi * POLICY_MULTIPLIERS['middle']['q_mult']
    print(f"  [middle] p={p_mi:.6f} (1.5x HI p), q={q_mi:.6f}")

    # Low-income: largest subsidy -> p most increased, q lower
    p_li = p_hi * POLICY_MULTIPLIERS['low']['p_mult']
    q_li = LITERATURE_Q['low'] if CALIBRATION_MODE == 'hybrid' else q_hi * POLICY_MULTIPLIERS['low']['q_mult']
    print(f"  [low]    p={p_li:.6f} (2.5x HI p), q={q_li:.6f}")

    # Store final parameters
    params = {
        'high': {'p': p_hi, 'q': q_hi, 'm': S3_PARAMS['high']['m']},
        'middle': {'p': p_mi, 'q': q_mi, 'm': S3_PARAMS['middle']['m']},
        'low': {'p': p_li, 'q': q_li, 'm': S3_PARAMS['low']['m']},
    }

    # ---- Step 3: Project adoption curves ----
    print("\n--- Step 3: Projecting Adoption Curves (2024-2050) ---")

    # Get Y0 for each group (2023 adoption level)
    Y0 = {
        'high': HISTORICAL_ADOPTION['high'][CALIBRATION_END],
        'middle': HISTORICAL_ADOPTION['middle'][CALIBRATION_END],
        'low': HISTORICAL_ADOPTION['low'][CALIBRATION_END],
    }

    # Run projections
    projections = {}
    for group in ['high', 'middle', 'low']:
        proj = run_projection(
            params[group]['p'], params[group]['q'], params[group]['m'],
            Y0[group], PROJECTION_START, PROJECTION_END
        )
        # Prepend historical data
        for y, v in HISTORICAL_ADOPTION[group].items():
            proj[y] = v
        projections[group] = proj

        # Print key milestones
        for milestone_year in [2030, 2040, 2050]:
            val = proj.get(milestone_year, 0) * 100
            print(f"  [{group}] {milestone_year}: {val:.2f}%")

    # ---- Step 4: Project household counts ----
    print("\n--- Step 4: Projecting Household Counts ---")
    hh_projected = {}
    for group in ['high', 'middle', 'low']:
        hh_projected[group] = project_hh_counts(
            HH_COUNTS[group], HH_GROWTH_RATE, PROJECTION_START, PROJECTION_END
        )

    # ---- Step 5: Calculate capacity ----
    print("\n--- Step 5: Capacity Summary ---")
    for milestone_year in [2030, 2040, 2050]:
        total_cap = 0
        for group in ['high', 'middle', 'low']:
            adoption = projections[group].get(milestone_year, 0)
            hh = hh_projected[group].get(milestone_year, 0)
            cap = adoption * hh * AVG_SYSTEM_SIZE[group] / 1000
            total_cap += cap
            print(f"  [{group}] {milestone_year}: {cap:.1f} MW "
                  f"({adoption*100:.1f}% × {hh:.0f} HH × {AVG_SYSTEM_SIZE[group]} kW)")
        print(f"  TOTAL {milestone_year}: {total_cap:.1f} MW\n")

    # ---- Step 6: Sensitivity analysis ----
    print("--- Step 6: Sensitivity Analysis (±30%) ---")
    sensitivity = {}
    for group in ['high', 'middle', 'low']:
        sensitivity[group] = run_sensitivity(
            params[group]['p'], params[group]['q'], params[group]['m'],
            Y0[group], PROJECTION_START, PROJECTION_END, variation=0.30
        )
        base_2050 = sensitivity[group]['base'].get(2050, 0) * 100
        high_2050 = sensitivity[group]['high_p_high_q'].get(2050, 0) * 100
        low_2050 = sensitivity[group]['low_p_low_q'].get(2050, 0) * 100
        print(f"  [{group}] 2050 range: {low_2050:.1f}% - {base_2050:.1f}% - {high_2050:.1f}%")

    # ---- Step 7: Generate outputs ----
    print("\n--- Step 7: Generating Outputs ---")

    csv_path = os.path.join(output_dir, 's3_bass_diffusion_results.csv')
    generate_csv(projections, hh_projected, csv_path)
    generate_plots(projections, sensitivity, hh_projected, output_dir)

    # ---- Print parameter summary ----
    print("\n" + "=" * 70)
    print("PARAMETER SUMMARY")
    print("=" * 70)
    print(f"{'Group':<12} {'p':>10} {'q':>10} {'m':>8} {'Y0':>10}")
    print("-" * 52)
    for group in ['high', 'middle', 'low']:
        print(f"{group:<12} {params[group]['p']:>10.6f} {params[group]['q']:>10.6f} "
              f"{params[group]['m']*100:>7.1f}% {Y0[group]*100:>9.4f}%")

    print("\n" + "=" * 70)
    print("DONE. Check output files in:", output_dir)
    print("=" * 70)

    return projections, params, sensitivity


if __name__ == '__main__':
    main()
