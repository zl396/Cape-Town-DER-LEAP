"""
Unmet Requirements Analysis: Updated LMI GHS vs Updated BAU GHS
================================================================
Calculates yearly energy balance and unmet requirements (including negative/surplus)
for both scenarios, using LEAP exported data + corrected SSEG capacity.

Key insight: Only SSEG capacity differs on supply side. All other generation is identical.
So: ΔUnmet = ΔDemand - ΔSSEG_generation

Units:
- Demand TFEC in Excel: Gigajoules (verified)
- Supply Historical Production: kWh (Eskom) or GWh (SSEG)
- Output: all converted to GWh
"""

import openpyxl
import csv
import os

# ============================================================
# SSEG Capacity (MW) - corrected values from LEAP
# (Excel export had identical values for both; these are the actual scenario-specific values)
# ============================================================
SSEG_CAPACITY_LMI = {
    2018: 10, 2019: 18, 2020: 33, 2021: 60, 2022: 110, 2023: 165,
    2024: 246, 2025: 339, 2026: 439, 2027: 539, 2028: 632, 2029: 713,
    2030: 780, 2035: 954, 2040: 1036, 2045: 1107, 2050: 1182
}

SSEG_CAPACITY_BAU = {
    2018: 10, 2019: 18, 2020: 33, 2021: 60, 2022: 109, 2023: 165,
    2024: 231, 2025: 303, 2026: 377, 2027: 445, 2028: 505, 2029: 553,
    2030: 590, 2035: 687, 2040: 741, 2045: 792, 2050: 845
}

SSEG_MAX_AVAILABILITY = 0.196  # 19.6% from LEAP data
HOURS_PER_YEAR = 8760


def interpolate_capacity(capacity_dict, year):
    """Linear interpolation for years between defined points."""
    years = sorted(capacity_dict.keys())
    if year in capacity_dict:
        return capacity_dict[year]
    for i in range(len(years) - 1):
        if years[i] < year < years[i + 1]:
            y1, y2 = years[i], years[i + 1]
            v1, v2 = capacity_dict[y1], capacity_dict[y2]
            return v1 + (v2 - v1) * (year - y1) / (y2 - y1)
    return capacity_dict[years[-1]]


def sseg_generation_gwh(capacity_mw):
    """Calculate SSEG annual generation in GWh from capacity (MW)."""
    return capacity_mw * HOURS_PER_YEAR * SSEG_MAX_AVAILABILITY / 1000


def extract_scenario_data(filepath, scenario_name):
    """Extract demand and supply data from LEAP Excel export."""
    wb = openpyxl.load_workbook(filepath, data_only=True)
    ws = wb['Export']

    data = {}
    for row in ws.iter_rows(min_row=3, max_row=ws.max_row, values_only=False):
        vals = [c.value for c in row]
        branch = vals[4]
        variable = vals[5]
        scenario = vals[6]
        units = vals[9]

        if scenario != scenario_name:
            continue

        key = (branch, variable)
        year_data = {}
        for y in range(2018, 2051):
            v = vals[12 + (y - 2018)]
            year_data[y] = v if v is not None else 0
        data[key] = {'units': units, 'data': year_data}

    return data


def calc_total_demand_gwh(scenario_data):
    """Sum demand TFEC across all sectors, convert GJ → GWh."""
    demand_branches = [
        'Demand\\Households',
        'Demand\\LPUs',
        'Demand\\SPUs',
        'Demand\\Municipality'
    ]
    total = {}
    for y in range(2018, 2051):
        total[y] = 0
    for branch in demand_branches:
        key = (branch, 'Total Final Energy Consumption')
        if key in scenario_data:
            for y in range(2018, 2051):
                # TFEC is in GJ; convert to GWh: 1 GWh = 3,600,000 GJ... no
                # 1 GWh = 3,600 GJ (1 GWh = 1e6 kWh, 1 kWh = 0.0036 GJ)
                # So GJ → GWh = GJ / 3600
                total[y] += scenario_data[key]['data'][y] / 3600
    return total


def calc_total_demand_by_sector_gwh(scenario_data):
    """Get demand by sector in GWh."""
    demand_branches = {
        'Households': 'Demand\\Households',
        'LPUs': 'Demand\\LPUs',
        'SPUs': 'Demand\\SPUs',
        'Municipality': 'Demand\\Municipality'
    }
    result = {}
    for name, branch in demand_branches.items():
        key = (branch, 'Total Final Energy Consumption')
        if key in scenario_data:
            result[name] = {}
            for y in range(2018, 2051):
                result[name][y] = scenario_data[key]['data'][y] / 3600
    return result


def calc_non_sseg_supply_gwh(scenario_data):
    """Sum Historical Production from all non-SSEG generation, convert to GWh.

    Note: Historical Production values for future years are LEAP's extrapolated
    input assumptions, not dispatch results. This is an approximation.
    """
    total = {}
    for y in range(2018, 2051):
        total[y] = 0

    for (branch, variable), val in scenario_data.items():
        if variable != 'Historical Production':
            continue
        if 'Transformation' not in branch:
            continue
        if 'SSEG' in branch:
            continue  # We handle SSEG separately with corrected values

        units = val['units']
        for y in range(2018, 2051):
            v = val['data'][y]
            if units == 'Kilowatt-Hour':
                total[y] += v / 1e6  # kWh → GWh
            elif units == 'Gigawatt-Hour':
                total[y] += v
            elif units == 'Megawatt-Hour':
                total[y] += v / 1e3

    return total


def get_td_loss_rate(scenario_data):
    """Get T&D loss rate from data."""
    key = ('Transformation\\Transmission and Distribution\\Processes\\Electricity', 'Losses')
    if key in scenario_data:
        val = scenario_data[key]['data']
        # Return as fraction (e.g., 8.5 → 0.085)
        return {y: val[y] / 100 if val[y] else 0.085 for y in range(2018, 2051)}
    # Default 8.5% if not found
    return {y: 0.085 for y in range(2018, 2051)}


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(script_dir)

    lmi_file = os.path.join(repo_dir, 'leap SCENARIO.xlsx')
    bau_file = os.path.join(repo_dir, 'LEAP Scenario Updated BAU.xlsx')

    print("Reading LEAP exports...")
    lmi_data = extract_scenario_data(lmi_file, 'Updated LMI GHS')
    bau_data = extract_scenario_data(bau_file, 'Updated BAU GHS')

    print(f"LMI data: {len(lmi_data)} entries")
    print(f"BAU data: {len(bau_data)} entries")

    # Calculate demand
    lmi_demand = calc_total_demand_gwh(lmi_data)
    bau_demand = calc_total_demand_gwh(bau_data)

    # Calculate non-SSEG supply (identical for both scenarios)
    non_sseg_supply = calc_non_sseg_supply_gwh(lmi_data)

    # Calculate SSEG generation with corrected capacity values
    lmi_sseg = {}
    bau_sseg = {}
    for y in range(2018, 2051):
        lmi_cap = interpolate_capacity(SSEG_CAPACITY_LMI, y)
        bau_cap = interpolate_capacity(SSEG_CAPACITY_BAU, y)
        lmi_sseg[y] = sseg_generation_gwh(lmi_cap)
        bau_sseg[y] = sseg_generation_gwh(bau_cap)

    # T&D losses
    td_loss = get_td_loss_rate(lmi_data)

    # Calculate total supply delivered (after T&D losses)
    # Total generation = non-SSEG + SSEG
    # Delivered = Total generation × (1 - loss_rate)
    # Note: SSEG (distributed) may bypass T&D losses partially, but LEAP treats it
    # through the Distributed Generation module. For simplicity, we apply losses uniformly.
    # Actually, in LEAP, distributed generation feeds directly to demand (no T&D loss).
    # Only centralized generation goes through T&D.

    results = []
    print("\n" + "=" * 120)
    print(f"{'Year':>4} | {'LMI Demand':>11} | {'BAU Demand':>11} | {'ΔDemand':>10} | "
          f"{'Non-SSEG':>10} | {'LMI SSEG':>9} | {'BAU SSEG':>9} | "
          f"{'LMI Unmet':>10} | {'BAU Unmet':>10} | {'ΔUnmet':>10}")
    print(f"{'':>4} | {'(GWh)':>11} | {'(GWh)':>11} | {'(GWh)':>10} | "
          f"{'(GWh)':>10} | {'(GWh)':>9} | {'(GWh)':>9} | "
          f"{'(GWh)':>10} | {'(GWh)':>10} | {'(GWh)':>10}")
    print("-" * 120)

    for y in range(2018, 2051):
        loss = td_loss[y]

        # Centralized supply delivered (after T&D losses)
        central_delivered = non_sseg_supply[y] * (1 - loss)

        # SSEG delivered directly (no T&D loss for distributed generation)
        lmi_sseg_delivered = lmi_sseg[y]
        bau_sseg_delivered = bau_sseg[y]

        # Total delivered
        lmi_total_supply = central_delivered + lmi_sseg_delivered
        bau_total_supply = central_delivered + bau_sseg_delivered

        # Unmet = Demand - Supply (negative = surplus/stranded)
        lmi_unmet = lmi_demand[y] - lmi_total_supply
        bau_unmet = bau_demand[y] - bau_total_supply

        delta_demand = lmi_demand[y] - bau_demand[y]
        delta_unmet = lmi_unmet - bau_unmet

        results.append({
            'Year': y,
            'LMI_Demand_GWh': round(lmi_demand[y], 2),
            'BAU_Demand_GWh': round(bau_demand[y], 2),
            'Delta_Demand_GWh': round(delta_demand, 2),
            'NonSSEG_Supply_GWh': round(non_sseg_supply[y], 2),
            'LMI_SSEG_GWh': round(lmi_sseg[y], 2),
            'BAU_SSEG_GWh': round(bau_sseg[y], 2),
            'Central_Delivered_GWh': round(central_delivered, 2),
            'LMI_Total_Supply_GWh': round(lmi_total_supply, 2),
            'BAU_Total_Supply_GWh': round(bau_total_supply, 2),
            'LMI_Unmet_GWh': round(lmi_unmet, 2),
            'BAU_Unmet_GWh': round(bau_unmet, 2),
            'Delta_Unmet_GWh': round(delta_unmet, 2),
            'TD_Loss_Pct': round(loss * 100, 2)
        })

        print(f"{y:>4} | {lmi_demand[y]:>11.2f} | {bau_demand[y]:>11.2f} | {delta_demand:>10.2f} | "
              f"{non_sseg_supply[y]:>10.2f} | {lmi_sseg[y]:>9.2f} | {bau_sseg[y]:>9.2f} | "
              f"{lmi_unmet:>10.2f} | {bau_unmet:>10.2f} | {delta_unmet:>10.2f}")

    # Write CSV
    csv_path = os.path.join(script_dir, 'unmet_requirements_comparison.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\nCSV saved to: {csv_path}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for y in [2025, 2030, 2035, 2040, 2045, 2050]:
        r = [x for x in results if x['Year'] == y][0]
        print(f"\n{y}:")
        print(f"  LMI Unmet: {r['LMI_Unmet_GWh']:>10.2f} GWh  ({'SURPLUS' if r['LMI_Unmet_GWh'] < 0 else 'DEFICIT'})")
        print(f"  BAU Unmet: {r['BAU_Unmet_GWh']:>10.2f} GWh  ({'SURPLUS' if r['BAU_Unmet_GWh'] < 0 else 'DEFICIT'})")
        print(f"  ΔUnmet:    {r['Delta_Unmet_GWh']:>10.2f} GWh  (LMI - BAU)")
        print(f"  ΔSSEG:     {r['LMI_SSEG_GWh'] - r['BAU_SSEG_GWh']:>10.2f} GWh  (additional DER generation)")


if __name__ == '__main__':
    main()
