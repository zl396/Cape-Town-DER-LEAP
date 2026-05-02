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
    'BAU':                 {'color': '#666666', 'label': 'BAU'},
    'LMI':                 {'color': '#2A9D8F', 'label': 'LMI Subsidy'},
    'Pro-solar':           {'color': '#E9C46A', 'label': 'Pro-Solar'},
    'Utility Protection':  {'color': '#E76F51', 'label': 'Utility Protection'},
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
        2018: 9.549, 2019: 18.073, 2020: 33.162, 2021: 59.787, 2022: 108.707,
        2023: 165.050, 2024: 230.948, 2025: 350.945, 2026: 480.678, 2027: 611.136,
        2028: 732.659, 2029: 799.597, 2030: 843.153, 2031: 875.751, 2032: 901.449,
        2033: 922.988, 2034: 942.076, 2035: 959.728, 2036: 976.529, 2037: 993.858,
        2038: 1011.036, 2039: 1027.936, 2040: 1044.631, 2041: 1061.176,
        2042: 1077.423, 2043: 1093.577, 2044: 1109.688, 2045: 1125.784,
        2046: 1141.893, 2047: 1158.040, 2048: 1174.248, 2049: 1190.536, 2050: 1206.923
    },
    'Utility Protection': {
        2018: 9.55, 2019: 18.06, 2020: 33.02, 2021: 59.83, 2022: 108.64,
        2023: 164.95, 2024: 183.689, 2025: 200.576, 2026: 215.733, 2027: 229.219,
        2028: 241.075, 2029: 251.406, 2030: 260.383, 2031: 268.212, 2032: 275.109,
        2033: 281.273, 2034: 286.874, 2035: 292.057, 2036: 296.934, 2037: 301.594,
        2038: 306.105, 2039: 310.520, 2040: 314.878, 2041: 319.207, 2042: 323.530,
        2043: 327.863, 2044: 332.219, 2045: 336.607, 2046: 341.033, 2047: 345.503,
        2048: 350.022, 2049: 354.592, 2050: 359.216
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


def load_all_unmet():
    """Load Unmet Requirements for all 4 scenarios."""
    return {
        'BAU': extract_bau_unmet(),
        'LMI': extract_single_sheet_unmet('LMI Energy Balance.xlsx'),
        'Pro-solar': extract_single_sheet_unmet('Updated Pro Solar.xlsx'),
        'Utility Protection': extract_single_sheet_unmet('Updated UT.xlsx'),
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
    ax.legend(fontsize=11, loc='lower right')
    ax.set_xlim(2018, 2050)
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))

    # Region labels — position further from x-axis to avoid crowding
    ax.text(2019, 200, 'Surplus Generation', fontsize=10, color='green',
            ha='left', va='bottom', alpha=0.7, fontweight='bold')
    ax.text(2019, -200, 'Load Shedding', fontsize=10, color='red',
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
