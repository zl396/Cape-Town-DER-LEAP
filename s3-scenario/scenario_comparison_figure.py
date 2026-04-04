"""
Generate two figures comparing 4 LEAP scenarios:
  1. Projected SSEG Installed Capacity by Scenario (2018-2050)
  2. Projected Unmet Electricity Requirements by Scenario (2018-2050)

Data sources:
  - Unmet Requirements: LEAP Energy Balance exports (GWh)
  - SSEG Capacity: user-provided Interp values from LEAP Data View (MW)
"""

import os
import csv
import openpyxl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
YEARS = list(range(2018, 2051))

# ============================================================
# Color scheme (consistent across both figures)
# ============================================================
SCENARIO_STYLE = {
    'BAU':                 {'color': '#888888', 'label': 'BAU'},
    'LMI':                 {'color': '#2166AC', 'label': 'Updated LMI GHS'},
    'Pro-solar':           {'color': '#1B7837', 'label': 'Pro-solar'},
    'Utility Protection':  {'color': '#B2182B', 'label': 'Utility Protection'},
}

# ============================================================
# SSEG Exogenous Capacity (MW) — from LEAP Data View
# ============================================================
SSEG_CAPACITY = {
    'BAU': {
        2018: 10, 2019: 18, 2020: 33, 2021: 60, 2022: 109, 2023: 165,
        2024: 231, 2025: 303, 2026: 377, 2027: 445, 2028: 505, 2029: 553,
        2030: 590, 2035: 687, 2040: 741, 2045: 792, 2050: 845
    },
    'LMI': {
        2018: 10, 2019: 18, 2020: 33, 2021: 60, 2022: 110, 2023: 165,
        2024: 246, 2025: 339, 2026: 439, 2027: 539, 2028: 632, 2029: 713,
        2030: 780, 2035: 954, 2040: 1036, 2045: 1107, 2050: 1182
    },
    'Pro-solar': {
        2018: 19.567, 2019: 27.524, 2020: 38.341, 2021: 52.437, 2022: 70.407,
        2023: 92.510, 2024: 118.287, 2025: 148.191, 2026: 181.837, 2027: 219.626,
        2028: 262.603, 2029: 309.182, 2030: 361.788, 2031: 421.808, 2032: 490.308,
        2033: 567.733, 2034: 653.354, 2035: 744.964, 2036: 839.220, 2037: 933.151,
        2038: 1023.608, 2039: 1108.596, 2040: 1186.831, 2041: 1257.304,
        2042: 1319.278, 2043: 1372.550, 2044: 1417.593, 2045: 1455.453,
        2046: 1487.463, 2047: 1506.441, 2048: 1522.879, 2049: 1537.071, 2050: 1551.358
    },
    'Utility Protection': {
        2018: 19.567, 2019: 27.524, 2020: 38.341, 2021: 52.437, 2022: 70.407,
        2023: 92.510, 2024: 118.290, 2025: 121.631, 2026: 124.754, 2027: 127.710,
        2028: 130.567, 2029: 133.394, 2030: 136.255, 2031: 139.336, 2032: 142.677,
        2033: 146.325, 2034: 150.335, 2035: 154.770, 2036: 159.701, 2037: 165.210,
        2038: 171.385, 2039: 178.325, 2040: 186.133, 2041: 194.923, 2042: 204.809,
        2043: 215.914, 2044: 228.362, 2045: 242.280, 2046: 257.801, 2047: 275.060,
        2048: 294.198, 2049: 315.363, 2050: 338.712
    },
}


def interp_capacity(cap_dict, year):
    """Linear interpolation between defined capacity points."""
    keys = sorted(cap_dict.keys())
    if year in cap_dict:
        return cap_dict[year]
    if year <= keys[0]:
        return cap_dict[keys[0]]
    if year >= keys[-1]:
        return cap_dict[keys[-1]]
    for i in range(len(keys) - 1):
        if keys[i] < year < keys[i + 1]:
            y1, y2 = keys[i], keys[i + 1]
            v1, v2 = cap_dict[y1], cap_dict[y2]
            return v1 + (v2 - v1) * (year - y1) / (y2 - y1)


def extract_bau_unmet():
    """Extract BAU Unmet from year-by-year Energy Balance sheets (Book7/8/9)."""
    unmet = {}
    for fname in ['Book7.xlsx', 'Book8.xlsx', 'Book9.xlsx']:
        path = os.path.join(REPO_DIR, fname)
        if not os.path.exists(path):
            continue
        wb = openpyxl.load_workbook(path, data_only=True)
        for sn in wb.sheetnames:
            year = int(sn.split('|')[1])
            ws = wb[sn]
            for r in range(1, ws.max_row + 1):
                vals = [c.value for c in ws[r]]
                if vals[0] == 'Unmet Requirements':
                    unmet[year] = vals[-1]
    return unmet


def extract_single_sheet_unmet(filename):
    """Extract Unmet from single-sheet Energy Balance (years as columns)."""
    path = os.path.join(REPO_DIR, filename)
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[wb.sheetnames[0]]
    unmet_row = [c.value for c in ws[17]]
    unmet = {}
    for i in range(1, len(unmet_row)):
        year = 2018 + (i - 1)
        if year <= 2050 and unmet_row[i] is not None:
            unmet[year] = unmet_row[i]
    return unmet


# Pro-solar corrected Unmet Requirements (GWh) — LEAP export clipped surplus to 0;
# these are the actual values provided from LEAP directly.
PROSOLAR_UNMET_OVERRIDE = {
    2018: 0, 2019: -3.24, 2020: -25.12, 2021: -38.59, 2022: -47.02,
    2023: -59.60, 2024: 1732.32, 2025: 1284.23, 2026: 1405.42, 2027: 1418.85,
    2028: 1185.28, 2029: 1172.93, 2030: 1492.31, 2031: 1426.50, 2032: 1098.30,
    2033: 922.46, 2034: 652.05, 2035: 203.55, 2036: -118.42, 2037: -152.60,
    2038: -191.51, 2039: -233.97, 2040: -278.25, 2041: -321.74, 2042: -362.70,
    2043: -399.58, 2044: -431.65, 2045: -459.01, 2046: -482.04, 2047: -493.03,
    2048: -502.64, 2049: -511.95, 2050: -521.48,
}


def load_all_unmet():
    """Load Unmet Requirements for all 4 scenarios."""
    return {
        'BAU': extract_bau_unmet(),
        'LMI': extract_single_sheet_unmet('LMI Energy Balance.xlsx'),
        'Pro-solar': PROSOLAR_UNMET_OVERRIDE,
        'Utility Protection': extract_single_sheet_unmet('Utility Protection Energy Balance.xlsx'),
    }


def plot_sseg_capacity(output_path):
    """Figure 1: SSEG Installed Capacity by Scenario."""
    fig, ax = plt.subplots(figsize=(10, 6))

    for name in ['BAU', 'LMI', 'Pro-solar', 'Utility Protection']:
        cap_data = SSEG_CAPACITY[name]
        ys = [interp_capacity(cap_data, y) for y in YEARS]
        style = SCENARIO_STYLE[name]
        ax.plot(YEARS, ys, color=style['color'], linewidth=2, label=style['label'])

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('SSEG Installed Capacity (MW)', fontsize=12)
    ax.set_title('Projected SSEG Installed Capacity by Scenario (2018–2050)', fontsize=14)
    ax.legend(fontsize=11, loc='upper left')
    ax.set_xlim(2018, 2050)
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))

    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved: {output_path}')


def plot_unmet_requirements(all_unmet, output_path):
    """Figure 2: Supply-Demand Balance by Scenario (flipped: positive=surplus, negative=deficit)."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Zero line
    ax.axhline(y=0, color='black', linewidth=0.8, linestyle='-')

    # Plot order: largest absolute values first so smaller fills stay visible
    plot_order = ['Utility Protection', 'Pro-solar', 'BAU', 'LMI']

    for name in plot_order:
        unmet = all_unmet[name]
        # Flip sign: positive = surplus, negative = deficit (load shedding)
        balance = [-unmet.get(y, 0) for y in YEARS]
        style = SCENARIO_STYLE[name]

        # Fill between zero and the line
        ax.fill_between(YEARS, 0, balance, alpha=0.15, color=style['color'])
        ax.plot(YEARS, balance, color=style['color'], linewidth=2, label=style['label'])

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Supply–Demand Balance (GWh)', fontsize=12)
    ax.set_title('Projected Supply–Demand Balance by Scenario (2018–2050)', fontsize=14)
    ax.legend(fontsize=11, loc='lower left')
    ax.set_xlim(2018, 2050)
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))

    # Region labels
    ax.text(2019, 50, 'Surplus Generation', fontsize=10, color='green',
            ha='left', va='bottom', alpha=0.7, fontweight='bold')
    ax.text(2019, -50, 'Load Shedding', fontsize=10, color='red',
            ha='left', va='top', alpha=0.7, fontweight='bold')

    fig.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved: {output_path}')


def write_csv(all_unmet, output_path):
    """Write all 4 scenarios to CSV."""
    rows = []
    for y in YEARS:
        row = {'Year': y}
        for name in ['BAU', 'LMI', 'Pro-solar', 'Utility Protection']:
            row[f'{name}_SSEG_MW'] = round(interp_capacity(SSEG_CAPACITY[name], y), 1)
            row[f'{name}_Unmet_GWh'] = round(all_unmet[name].get(y, 0), 2)
        rows.append(row)

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f'Saved: {output_path}')


def main():
    print('Loading Unmet Requirements from LEAP Energy Balance exports...')
    all_unmet = load_all_unmet()

    for name, data in all_unmet.items():
        print(f'  {name}: {len(data)} years loaded')

    plot_sseg_capacity(os.path.join(SCRIPT_DIR, 'scenario_sseg_capacity.png'))
    plot_unmet_requirements(all_unmet, os.path.join(SCRIPT_DIR, 'scenario_supply_demand_balance.png'))
    write_csv(all_unmet, os.path.join(SCRIPT_DIR, 'unmet_requirements_comparison.csv'))

    # Print summary
    print('\n=== Summary ===')
    print(f'{"Scenario":<22} {"2030 SSEG":>10} {"2050 SSEG":>10} {"2024-33 Deficit":>15} {"2034-50 Surplus":>15}')
    print(f'{"":22} {"(MW)":>10} {"(MW)":>10} {"(GWh)":>15} {"(GWh)":>15}')
    print('-' * 75)
    for name in ['BAU', 'LMI', 'Pro-solar', 'Utility Protection']:
        sseg_2030 = interp_capacity(SSEG_CAPACITY[name], 2030)
        sseg_2050 = interp_capacity(SSEG_CAPACITY[name], 2050)
        deficit = sum(max(0, all_unmet[name].get(y, 0)) for y in range(2024, 2034))
        surplus = sum(min(0, all_unmet[name].get(y, 0)) for y in range(2034, 2051))
        print(f'{name:<22} {sseg_2030:>10.0f} {sseg_2050:>10.0f} {deficit:>15.0f} {surplus:>15.0f}')


if __name__ == '__main__':
    main()
