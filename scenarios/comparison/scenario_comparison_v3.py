"""
v3 — Generate scenario comparison figures using the May 1 fresh exports
(after Eskom IPP capacity was restored in LEAP).

Inputs (in repo root):
  BAU EB v3.xlsx  (multi-sheet — explicitly read 'Energy Balance')
  LMI EB v3.xlsx
  Pro Solar EB v3.xlsx
  UP EB v3.xlsx

Outputs (in s3-scenario/):
  scenario_sseg_capacity_v3.png         — 4-scenario SSEG capacity
  scenario_energy_balance_v3.png        — 3-panel: Production / Imports / Unmet
  scenario_comparison_v3.csv            — long-format data dump
"""

import os
import csv
import openpyxl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# scenarios/comparison/ → up 2 levels to repo root
REPO_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
YEARS = list(range(2018, 2051))

SCENARIO_STYLE = {
    'BAU':                {'color': '#666666', 'label': 'BAU'},
    'LMI':                {'color': '#2A9D8F', 'label': 'LMI Subsidy'},
    'Pro-solar':          {'color': '#E9C46A', 'label': 'Pro-Solar'},
    'Utility Protection': {'color': '#E76F51', 'label': 'Utility Protection'},
}

DATA_DIR = os.path.join(REPO_DIR, 'data', 'current')
SCENARIO_FILES = {
    'BAU':                ('BAU EB v3.xlsx',       'Energy Balance'),
    'LMI':                ('LMI EB v3.xlsx',       None),
    'Pro-solar':          ('Pro Solar EB v3.xlsx', None),
    'Utility Protection': ('UP EB v3.xlsx',        None),
}

# SSEG Exogenous Capacity (MW) — hardcoded from LEAP Data View
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


def load_energy_balance(filename, sheet_name=None):
    """Load Production / Imports / Unmet from a single-sheet 'Fuels: All' file."""
    path = os.path.join(DATA_DIR, filename)
    wb = openpyxl.load_workbook(path, data_only=True)
    sn = sheet_name or wb.sheetnames[0]
    if sn not in wb.sheetnames:
        raise KeyError(f"Sheet {sn!r} not in {filename}; sheets: {wb.sheetnames}")
    ws = wb[sn]
    header = ws.cell(row=2, column=1).value or ''
    out = {'Production': {}, 'Imports': {}, 'Unmet Requirements': {}}
    for r in range(1, ws.max_row + 1):
        label = ws.cell(row=r, column=1).value
        if label not in out:
            continue
        for c in range(2, ws.max_column + 1):
            year = 2018 + (c - 2)
            if year > 2050:
                break
            v = ws.cell(row=r, column=c).value
            if v is not None:
                out[label][year] = v
    return out, header


def load_all():
    series = {}
    headers = {}
    for name, (fname, sheet) in SCENARIO_FILES.items():
        data, hdr = load_energy_balance(fname, sheet)
        series[name] = data
        headers[name] = hdr
    return series, headers


def fig_sseg_capacity(out_path):
    fig, ax = plt.subplots(figsize=(10, 6))
    for name in ['BAU', 'LMI', 'Pro-solar', 'Utility Protection']:
        cap = SSEG_CAPACITY[name]
        y = [interp_capacity(cap, yr) for yr in YEARS]
        ax.plot(YEARS, y, color=SCENARIO_STYLE[name]['color'],
                label=SCENARIO_STYLE[name]['label'], linewidth=2.4)
    ax.set_title('Projected SSEG Installed Capacity by Scenario, 2018–2050',
                 fontsize=13, loc='left')
    ax.set_xlabel('Year')
    ax.set_ylabel('SSEG capacity (MW)')
    ax.set_xlim(2018, 2050)
    ax.grid(alpha=0.3)
    ax.legend(loc='upper left', framealpha=0.95)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    fig.tight_layout()
    fig.savefig(out_path, dpi=140, bbox_inches='tight')
    plt.close(fig)


def fig_energy_balance(series, out_path):
    """3-panel diagnostic view (Production / Imports / Unmet)."""
    fig, axes = plt.subplots(3, 1, figsize=(11, 13), sharex=True)

    def to_xy(d):
        yrs = sorted(d.keys())
        return yrs, [d[y] for y in yrs]

    for ax, metric, title, ylabel in [
        (axes[0], 'Production',
         'Production (GWh) — SSEG + utility-scale generation',
         'Production (GWh)'),
        (axes[1], 'Imports',
         'Imports (GWh) — centralized grid (Eskom) supply to Cape Town',
         'Imports (GWh)'),
        (axes[2], 'Unmet Requirements',
         'Unmet Requirements (GWh) — positive = deficit, negative = surplus',
         'Unmet (GWh)'),
    ]:
        for name in ['BAU', 'LMI', 'Pro-solar', 'Utility Protection']:
            x, y = to_xy(series[name][metric])
            ax.plot(x, y, color=SCENARIO_STYLE[name]['color'],
                    label=SCENARIO_STYLE[name]['label'], linewidth=2.2)
        ax.set_title(title, fontsize=11, loc='left')
        ax.set_ylabel(ylabel)
        ax.grid(alpha=0.3)
        ax.set_xlim(2018, 2050)
        ax.axhline(0, color='#999', linewidth=0.5)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))

    axes[-1].set_xlabel('Year')
    axes[0].legend(loc='upper left', fontsize=10, framealpha=0.95)
    fig.suptitle(
        'Energy Balance by Scenario, 2018–2050 (fresh LEAP exports, May 1)',
        fontsize=13, y=0.995,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=140, bbox_inches='tight')
    plt.close(fig)


def fig_supply_demand_balance(series, out_path):
    """Single-panel supply-demand gap chart with shaded fill, matching the
    legacy publication-style figure. Sign convention: positive = surplus,
    negative = load shedding (i.e., -Unmet)."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Display order for layering: smallest line on top → plot in order so
    # outliers stay readable.  Use legend ordering matching the legacy figure
    # (UP, Pro-Solar, BAU, LMI).
    plot_order = ['Utility Protection', 'Pro-solar', 'BAU', 'LMI']

    for name in plot_order:
        unmet = series[name]['Unmet Requirements']
        yrs = sorted(unmet.keys())
        balance = [-unmet[y] for y in yrs]  # invert sign
        color = SCENARIO_STYLE[name]['color']
        ax.plot(yrs, balance, color=color,
                label=SCENARIO_STYLE[name]['label'], linewidth=2.2, zorder=3)
        ax.fill_between(yrs, 0, balance, color=color, alpha=0.18, zorder=2)

    ax.axhline(0, color='#444', linewidth=0.8, zorder=1)
    ax.set_xlim(2020, 2050)
    ax.set_xlabel('Year')
    ax.set_ylabel('Supply-Demand Balance (GWh)')
    ax.set_title('Projected Supply-Demand Balance by Scenario (2018–2050)',
                 fontsize=13)
    ax.grid(alpha=0.3, zorder=0)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))

    # Annotations
    ymin, ymax = ax.get_ylim()
    ax.text(2021, ymax * 0.65, 'Surplus Generation',
            color='#1B7837', fontsize=11, fontweight='bold', zorder=4)
    ax.text(2021, ymin * 0.55, 'Load Shedding',
            color='#B2182B', fontsize=11, fontweight='bold', zorder=4)

    ax.legend(loc='lower right', framealpha=0.95)
    fig.tight_layout()
    fig.savefig(out_path, dpi=140, bbox_inches='tight')
    plt.close(fig)


def write_csv(series, out_path):
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['scenario', 'year', 'sseg_mw', 'production_gwh',
                    'imports_gwh', 'unmet_gwh'])
        for name in ['BAU', 'LMI', 'Pro-solar', 'Utility Protection']:
            cap = SSEG_CAPACITY[name]
            data = series[name]
            for y in YEARS:
                w.writerow([
                    name, y,
                    f"{interp_capacity(cap, y):.2f}",
                    f"{data['Production'].get(y, ''):.2f}" if y in data['Production'] else '',
                    f"{data['Imports'].get(y, ''):.2f}" if y in data['Imports'] else '',
                    f"{data['Unmet Requirements'].get(y, ''):.2f}" if y in data['Unmet Requirements'] else '',
                ])


def main():
    series, headers = load_all()
    print('=== Source verification ===')
    for name, hdr in headers.items():
        print(f'  {name:<22}: {hdr}')

    sseg_path = os.path.join(SCRIPT_DIR, 'scenario_sseg_capacity_v3.png')
    eb_path   = os.path.join(SCRIPT_DIR, 'scenario_energy_balance_v3.png')
    sdb_path  = os.path.join(SCRIPT_DIR, 'scenario_supply_demand_balance_v3.png')
    csv_path  = os.path.join(SCRIPT_DIR, 'scenario_comparison_v3.csv')

    fig_sseg_capacity(sseg_path)
    fig_energy_balance(series, eb_path)
    fig_supply_demand_balance(series, sdb_path)
    write_csv(series, csv_path)

    print(f'\nSaved:')
    print(f'  {sseg_path}')
    print(f'  {eb_path}')
    print(f'  {sdb_path}')
    print(f'  {csv_path}')

    # Summary
    print('\n=== 2050 Summary ===')
    print(f"{'Scenario':<22} {'SSEG (MW)':>10} {'Prod':>9} {'Imports':>9} {'Unmet':>9}")
    for name in ['BAU', 'LMI', 'Pro-solar', 'Utility Protection']:
        sseg = interp_capacity(SSEG_CAPACITY[name], 2050)
        d = series[name]
        prod = d['Production'].get(2050, float('nan'))
        imp = d['Imports'].get(2050, float('nan'))
        unmet = d['Unmet Requirements'].get(2050, float('nan'))
        print(f"{name:<22} {sseg:>10,.0f} {prod:>9,.0f} {imp:>9,.0f} {unmet:>9,.0f}")


if __name__ == '__main__':
    main()
