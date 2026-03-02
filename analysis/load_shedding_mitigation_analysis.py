#!/usr/bin/env python3
"""
Cape Town DER Load Shedding Mitigation Analysis
ESM-01 Analysis Script

This script analyzes the potential of Distributed Energy Resources (DER) 
to mitigate load shedding in Cape Town under the S3 Progressive Subsidy scenario.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# ============================================================================
# CONSTANTS AND ASSUMPTIONS
# ============================================================================

# Load Shedding Parameters
LOAD_SHEDDING_STAGES = {
    1: 1000,  # MW
    2: 2000,
    3: 3000,
    4: 4000,
    5: 5000,
    6: 6000,
    7: 7000,
    8: 8000
}

# Peak load shedding hours (based on Eskom patterns)
PEAK_MORNING = (6, 9)    # 6am-9am
PEAK_EVENING = (17, 21)  # 5pm-9pm

# DER Capacity Projections (S3 Progressive Subsidy Scenario)
DER_PROJECTIONS = {
    2024: {'residential_MW': 104, 'total_MW': 159},
    2030: {'residential_MW': 522, 'total_MW': 576},
    2040: {'residential_MW': 893, 'total_MW': 1010},
    2050: {'residential_MW': 1033, 'total_MW': 1286}
}

# System parameters
SOLAR_CF_ANNUAL = 0.196  # 19.6% annual capacity factor
HOUSEHOLD_COUNT_2023 = 633000
HH_GROWTH_RATE = 0.013  # 1.3% CAGR

# Income group parameters
INCOME_GROUPS = {
    'high': {
        'saturation': 0.30,
        'avg_capacity_kW': 8,
        'battery_adoption': 0.70,  # 70% with storage
        'battery_capacity_kWh': 10
    },
    'middle': {
        'saturation': 0.25,
        'avg_capacity_kW': 5,
        'battery_adoption': 0.40,  # 40% with storage
        'battery_capacity_kWh': 7
    },
    'low': {
        'saturation': 0.15,
        'avg_capacity_kW': 3,
        'battery_adoption': 0.10,  # 10% with storage
        'battery_capacity_kWh': 5
    }
}

# Cape Town demand estimates (based on municipal utility data)
CAPE_TOWN_PEAK_DEMAND_MW = 4200  # Approximate peak demand
CAPE_TOWN_AVG_DEMAND_MW = 2800   # Average demand

# ============================================================================
# FUNCTION DEFINITIONS
# ============================================================================

def calculate_hourly_cf_simple():
    """Calculate simplified hourly capacity factors based on typical solar curve"""
    # Typical solar generation curve for Cape Town (summer average)
    hourly_cf = {
        0: 0.00, 1: 0.00, 2: 0.00, 3: 0.00, 4: 0.00, 5: 0.00,
        6: 0.10, 7: 0.30, 8: 0.50, 9: 0.65, 10: 0.75, 11: 0.85,
        12: 0.90, 13: 0.85, 14: 0.75, 15: 0.65, 16: 0.50, 17: 0.30,
        18: 0.15, 19: 0.05, 20: 0.00, 21: 0.00, 22: 0.00, 23: 0.00
    }
    return hourly_cf

def calculate_temporal_overlap():
    """
    Calculate temporal overlap between solar generation and load shedding
    """
    hourly_cf = calculate_hourly_cf_simple()
    
    morning_hours = range(PEAK_MORNING[0], PEAK_MORNING[1])
    evening_hours = range(PEAK_EVENING[0], PEAK_EVENING[1])
    
    # Average capacity factor during each period
    morning_cf = np.mean([hourly_cf[h] for h in morning_hours])
    evening_cf = np.mean([hourly_cf[h] for h in evening_hours])
    
    # Overall peak hours (combined morning + evening)
    all_peak_hours = list(morning_hours) + list(evening_hours)
    peak_cf = np.mean([hourly_cf[h] for h in all_peak_hours])
    
    return {
        'morning_cf': morning_cf,
        'evening_cf': evening_cf,
        'peak_combined_cf': peak_cf,
        'morning_hours': len(morning_hours),
        'evening_hours': len(evening_hours)
    }

def calculate_effective_der_capacity(der_capacity_mw, temporal_data):
    """
    Calculate effective DER capacity during load shedding windows
    
    WITHOUT storage: only direct solar generation during load shedding
    WITH storage: includes shifted solar energy
    """
    # Without storage - only real-time generation
    effective_without_storage = {
        'morning': der_capacity_mw * temporal_data['morning_cf'],
        'evening': der_capacity_mw * temporal_data['evening_cf'],
        'peak_combined': der_capacity_mw * temporal_data['peak_combined_cf']
    }
    
    # With storage - assume battery can shift daytime surplus to evening
    # Conservative assumption: 50% of midday excess can be stored for evening
    midday_cf = 0.85  # Peak midday CF
    storage_shift_efficiency = 0.45  # Round-trip efficiency + utilization
    
    # Assume avg 50% of DER systems have storage by 2030, ramping up
    evening_storage_boost = der_capacity_mw * midday_cf * storage_shift_efficiency
    
    effective_with_storage = {
        'morning': effective_without_storage['morning'],  # No storage benefit
        'evening': effective_without_storage['evening'] + evening_storage_boost,
        'peak_combined': (effective_without_storage['morning'] * 3 + 
                         (effective_without_storage['evening'] + evening_storage_boost) * 4) / 7
    }
    
    return {
        'without_storage': effective_without_storage,
        'with_storage': effective_with_storage
    }

def calculate_household_resilience(year, income_group_params):
    """
    Calculate what percentage of households can island during load shedding
    """
    households = HOUSEHOLD_COUNT_2023 * ((1 + HH_GROWTH_RATE) ** (year - 2023))
    
    results = {}
    total_islanding_capable = 0
    
    for group_name, params in income_group_params.items():
        group_size = households / 3  # Assume equal distribution
        
        # Households with solar
        solar_households = group_size * params['saturation']
        
        # Households with solar + battery (islanding capable)
        islanding_households = solar_households * params['battery_adoption']
        
        # Can they ride through Stage 4 (2.5 hours)?
        avg_household_load_kW = 2.0  # Conservative average
        load_shedding_duration_hours = 2.5
        energy_needed_kWh = avg_household_load_kW * load_shedding_duration_hours
        
        can_island_stage4 = islanding_households if params['battery_capacity_kWh'] >= energy_needed_kWh else 0
        
        results[group_name] = {
            'total_households': group_size,
            'solar_households': solar_households,
            'islanding_capable': islanding_households,
            'can_ride_stage4': can_island_stage4,
            'avg_battery_kWh': params['battery_capacity_kWh']
        }
        
        total_islanding_capable += islanding_households
    
    results['summary'] = {
        'total_households': households,
        'total_islanding_capable': total_islanding_capable,
        'islanding_percentage': (total_islanding_capable / households) * 100
    }
    
    return results

def calculate_system_level_impact(year, der_mw, effective_capacity):
    """
    Calculate system-level impact on Cape Town's load shedding burden
    """
    morning_reduction = effective_capacity['with_storage']['morning']
    evening_reduction = effective_capacity['with_storage']['evening']
    
    # Cape Town's share of national load shedding
    ct_share = 0.15
    
    results = {}
    for stage, national_mw in LOAD_SHEDDING_STAGES.items():
        ct_burden_mw = national_mw * ct_share
        
        morning_coverage = (morning_reduction / ct_burden_mw) * 100 if ct_burden_mw > 0 else 0
        evening_coverage = (evening_reduction / ct_burden_mw) * 100 if ct_burden_mw > 0 else 0
        
        results[f'stage_{stage}'] = {
            'national_mw': national_mw,
            'ct_burden_mw': ct_burden_mw,
            'morning_coverage_pct': morning_coverage,
            'evening_coverage_pct': evening_coverage
        }
    
    return results

def generate_projection_table(years=[2024, 2030, 2040, 2050]):
    """Generate comprehensive projection table across all years"""
    temporal_data = calculate_temporal_overlap()
    
    results = []
    
    for year in years:
        der_mw = DER_PROJECTIONS[year]['total_MW']
        
        effective = calculate_effective_der_capacity(der_mw, temporal_data)
        hh_resilience = calculate_household_resilience(year, INCOME_GROUPS)
        system_impact = calculate_system_level_impact(year, der_mw, effective)
        
        results.append({
            'year': year,
            'total_der_mw': der_mw,
            'effective_morning_no_storage': effective['without_storage']['morning'],
            'effective_evening_no_storage': effective['without_storage']['evening'],
            'effective_morning_with_storage': effective['with_storage']['morning'],
            'effective_evening_with_storage': effective['with_storage']['evening'],
            'islanding_households': hh_resilience['summary']['total_islanding_capable'],
            'islanding_pct': hh_resilience['summary']['islanding_percentage'],
            'stage4_morning_coverage': system_impact['stage_4']['morning_coverage_pct'],
            'stage4_evening_coverage': system_impact['stage_4']['evening_coverage_pct']
        })
    
    return pd.DataFrame(results)

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def main():
    print("="*80)
    print("Cape Town DER Load Shedding Mitigation Analysis")
    print("ESM-01 - Energy System Modeler")
    print("="*80)
    print()
    
    # Generate projection table
    print("Generating DER mitigation projections...")
    projections = generate_projection_table()
    
    print("\n" + "="*80)
    print("PROJECTION SUMMARY TABLE")
    print("="*80)
    print(projections.to_string(index=False))
    
    # Save detailed results
    output_file = '/Users/googam/Projects/Cape-Town-DER-LEAP/analysis/projections_detailed.json'
    
    temporal_data = calculate_temporal_overlap()
    detailed_results = {}
    for year in [2024, 2030, 2040, 2050]:
        der_mw = DER_PROJECTIONS[year]['total_MW']
        
        effective = calculate_effective_der_capacity(der_mw, temporal_data)
        hh_resilience = calculate_household_resilience(year, INCOME_GROUPS)
        system_impact = calculate_system_level_impact(year, der_mw, effective)
        
        detailed_results[str(year)] = {
            'der_capacity_mw': der_mw,
            'effective_capacity': effective,
            'household_resilience': hh_resilience,
            'system_impact': system_impact,
            'temporal_overlap': temporal_data
        }
    
    with open(output_file, 'w') as f:
        json.dump(detailed_results, f, indent=2, default=str)
    
    print(f"\n✓ Detailed results saved to: {output_file}")
    print("\n" + "="*80)
    print("KEY FINDINGS")
    print("="*80)
    
    print("\n1. TEMPORAL MISMATCH IS CRITICAL:")
    print(f"   - Morning peak (6-9am): {temporal_data['morning_cf']*100:.1f}% avg solar CF → moderate overlap")
    print(f"   - Evening peak (5-9pm): {temporal_data['evening_cf']*100:.1f}% avg solar CF → SEVERE mismatch")
    print("   - WITHOUT storage: DER provides minimal evening load shedding relief")
    
    print("\n2. STORAGE TRANSFORMS THE EQUATION:")
    print("   - With battery storage, evening coverage increases dramatically")
    print(f"   - 2030: {projections.loc[projections['year']==2030, 'effective_evening_with_storage'].values[0]:.0f} MW evening capacity (with storage)")
    print(f"   - 2030: {projections.loc[projections['year']==2030, 'effective_evening_no_storage'].values[0]:.0f} MW evening capacity (without storage)")
    
    print("\n3. HOUSEHOLD-LEVEL RESILIENCE:")
    print(f"   - 2024: {projections.loc[projections['year']==2024, 'islanding_pct'].values[0]:.1f}% of households can island")
    print(f"   - 2030: {projections.loc[projections['year']==2030, 'islanding_pct'].values[0]:.1f}% of households can island")
    print(f"   - 2050: {projections.loc[projections['year']==2050, 'islanding_pct'].values[0]:.1f}% of households can island")
    
    print("\n4. SYSTEM-LEVEL IMPACT (Stage 4 Load Shedding):")
    print(f"   - 2030 Morning: {projections.loc[projections['year']==2030, 'stage4_morning_coverage'].values[0]:.1f}% of CT burden covered")
    print(f"   - 2030 Evening: {projections.loc[projections['year']==2030, 'stage4_evening_coverage'].values[0]:.1f}% of CT burden covered")
    
    print("\n" + "="*80)
    print("Analysis complete. See analysis/der_load_shedding_analysis.md for full report.")
    print("="*80)
    
    # Save CSV for easy reference
    projections.to_csv('/Users/googam/Projects/Cape-Town-DER-LEAP/analysis/projections_summary.csv', index=False)
    print("\n✓ CSV summary saved to: /Users/googam/Projects/Cape-Town-DER-LEAP/analysis/projections_summary.csv")

if __name__ == "__main__":
    main()
