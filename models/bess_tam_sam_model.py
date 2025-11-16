"""
Global Battery Energy Storage Systems (BESS) - TAM/SAM Market Sizing Model
Top-down and bottom-up market size analysis with segmentation and growth projections
"""

import numpy as np
import pandas as pd

class BESS_Market_Model:
    """Comprehensive TAM/SAM model for global energy storage market"""

    def __init__(self):
        # Global electricity generation baseline (TWh)
        self.global_generation_2024 = 29000  # TWh

        # Renewable penetration forecast (% of generation)
        self.renewable_penetration = {
            2024: 0.30, 2025: 0.33, 2026: 0.36, 2027: 0.40, 2028: 0.44,
            2029: 0.48, 2030: 0.52, 2031: 0.55, 2032: 0.58, 2033: 0.60, 2034: 0.62, 2035: 0.65
        }

        # Storage attachment rate (GWh storage per GW renewable capacity)
        self.storage_attachment_hours = 4.5  # Average duration

        # Average system cost ($/kWh installed)
        self.system_costs = {
            2024: 300, 2025: 280, 2026: 260, 2027: 245, 2028: 230,
            2029: 220, 2030: 210, 2031: 205, 2032: 200, 2033: 195, 2034: 190, 2035: 185
        }

        # Segmentation
        self.segments = ['Utility-Scale', 'Commercial & Industrial', 'Residential']
        self.segment_split = {'Utility-Scale': 0.70, 'Commercial & Industrial': 0.20, 'Residential': 0.10}

        # Geographic regions
        self.regions = ['Americas', 'EMEA', 'Asia-Pacific']
        self.regional_split_2024 = {'Americas': 0.40, 'EMEA': 0.30, 'Asia-Pacific': 0.30}
        self.regional_growth_rates = {
            'Americas': 1.35,  # 35% CAGR
            'EMEA': 1.40,      # 40% CAGR
            'Asia-Pacific': 1.32  # 32% CAGR
        }

    def calculate_top_down_tam(self):
        """Top-down TAM based on renewable energy growth"""
        years = list(range(2024, 2036))
        results = []

        for year in years:
            # Global generation growth (1.5% annual)
            generation = self.global_generation_2024 * (1.015 ** (year - 2024))

            # Renewable share
            renewable_gen = generation * self.renewable_penetration[year]  # TWh

            # Renewable capacity (assuming 25% capacity factor average)
            renewable_capacity_gw = renewable_gen / (0.25 * 8.76)  # GW

            # Storage need (GWh)
            storage_gwh = renewable_capacity_gw * self.storage_attachment_hours

            # Market value ($B)
            avg_cost = self.system_costs[year]
            market_value_b = storage_gwh * avg_cost / 1000  # Convert to billions

            results.append({
                'Year': year,
                'Global Generation (TWh)': generation,
                'Renewable Generation (TWh)': renewable_gen,
                'Renewable Capacity (GW)': renewable_capacity_gw,
                'Storage TAM (GWh)': storage_gwh,
                'TAM Value ($B)': market_value_b,
                'Average Cost ($/kWh)': avg_cost
            })

        return pd.DataFrame(results)

    def calculate_bottom_up_tam(self):
        """Bottom-up TAM based on regional project pipelines and growth"""
        # Base 2024 market: 100 GWh deployed
        base_market_2024 = {'Americas': 40, 'EMEA': 30, 'Asia-Pacific': 30}  # GWh

        years = list(range(2024, 2036))
        results = []

        for year in years:
            year_offset = year - 2024
            regional_data = {}
            total_gwh = 0
            total_value = 0

            for region in self.regions:
                # Apply regional growth rate
                gwh = base_market_2024[region] * (self.regional_growth_rates[region] ** year_offset)
                value_b = gwh * self.system_costs[year] / 1000

                regional_data[f'{region} (GWh)'] = gwh
                regional_data[f'{region} ($B)'] = value_b
                total_gwh += gwh
                total_value += value_b

            results.append({
                'Year': year,
                **regional_data,
                'Total TAM (GWh)': total_gwh,
                'Total TAM ($B)': total_value
            })

        return pd.DataFrame(results)

    def calculate_sam(self):
        """Serviceable Addressable Market based on regulatory/economic viability"""
        # SAM filters:
        # - Regulatory approval: 85% of TAM
        # - Economic viability at current costs: 75% of approved projects
        # - Accessible markets (excluding restricted geographies): 90%

        sam_factor = 0.85 * 0.75 * 0.90  # ~57% of TAM

        tam_df = self.calculate_top_down_tam()
        sam_df = tam_df.copy()
        sam_df['SAM (GWh)'] = sam_df['Storage TAM (GWh)'] * sam_factor
        sam_df['SAM Value ($B)'] = sam_df['TAM Value ($B)'] * sam_factor

        return sam_df[['Year', 'Storage TAM (GWh)', 'SAM (GWh)', 'TAM Value ($B)', 'SAM Value ($B)']]

    def segment_analysis(self):
        """Break down TAM by market segment"""
        tam_df = self.calculate_top_down_tam()
        years = tam_df['Year'].values
        segments_data = []

        for year in years:
            total_gwh = tam_df[tam_df['Year'] == year]['Storage TAM (GWh)'].values[0]
            total_value = tam_df[tam_df['Year'] == year]['TAM Value ($B)'].values[0]

            row = {'Year': year}
            for segment, split in self.segment_split.items():
                row[f'{segment} (GWh)'] = total_gwh * split
                row[f'{segment} ($B)'] = total_value * split

            segments_data.append(row)

        return pd.DataFrame(segments_data)

    def calculate_cagr(self):
        """Calculate Compound Annual Growth Rates"""
        tam_df = self.calculate_top_down_tam()

        # Overall CAGR (2024-2030)
        tam_2024 = tam_df[tam_df['Year'] == 2024]['Storage TAM (GWh)'].values[0]
        tam_2030 = tam_df[tam_df['Year'] == 2030]['Storage TAM (GWh)'].values[0]
        cagr_2030 = (tam_2030 / tam_2024) ** (1/6) - 1

        # Extended CAGR (2024-2035)
        tam_2035 = tam_df[tam_df['Year'] == 2035]['Storage TAM (GWh)'].values[0]
        cagr_2035 = (tam_2035 / tam_2024) ** (1/11) - 1

        value_2024 = tam_df[tam_df['Year'] == 2024]['TAM Value ($B)'].values[0]
        value_2030 = tam_df[tam_df['Year'] == 2030]['TAM Value ($B)'].values[0]
        value_2035 = tam_df[tam_df['Year'] == 2035]['TAM Value ($B)'].values[0]

        cagr_value_2030 = (value_2030 / value_2024) ** (1/6) - 1
        cagr_value_2035 = (value_2035 / value_2024) ** (1/11) - 1

        return {
            'GWh CAGR 2024-2030': cagr_2030,
            'GWh CAGR 2024-2035': cagr_2035,
            'Value CAGR 2024-2030': cagr_value_2030,
            'Value CAGR 2024-2035': cagr_value_2035
        }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    model = BESS_Market_Model()

    print("=" * 80)
    print("BATTERY ENERGY STORAGE SYSTEMS (BESS) - TAM/SAM MARKET MODEL")
    print("=" * 80)
    print()

    # Top-down TAM
    print("1. TOP-DOWN TAM FORECAST (Renewable Energy-Driven)")
    print("-" * 80)
    tam_topdown = model.calculate_top_down_tam()
    print(tam_topdown.to_string(index=False))
    print()

    # Bottom-up TAM
    print("\n2. BOTTOM-UP TAM FORECAST (Regional Project Growth)")
    print("-" * 80)
    tam_bottomup = model.calculate_bottom_up_tam()
    print(tam_bottomup.to_string(index=False))
    print()

    # SAM Analysis
    print("\n3. SERVICEABLE ADDRESSABLE MARKET (SAM)")
    print("-" * 80)
    sam = model.calculate_sam()
    print(sam.to_string(index=False))
    print()

    # Segment breakdown
    print("\n4. MARKET SEGMENTATION")
    print("-" * 80)
    segments = model.segment_analysis()
    print(segments.to_string(index=False))
    print()

    # Growth rates
    print("\n5. COMPOUND ANNUAL GROWTH RATES (CAGR)")
    print("-" * 80)
    cagr = model.calculate_cagr()
    for metric, value in cagr.items():
        print(f"{metric}: {value:.1%}")
    print()

    # Export results
    print("\n6. EXPORTING RESULTS")
    print("-" * 80)
    tam_topdown.to_csv('/home/user/TDITG/models/bess_tam_topdown.csv', index=False)
    tam_bottomup.to_csv('/home/user/TDITG/models/bess_tam_bottomup.csv', index=False)
    sam.to_csv('/home/user/TDITG/models/bess_sam.csv', index=False)
    segments.to_csv('/home/user/TDITG/models/bess_segments.csv', index=False)

    print("✓ bess_tam_topdown.csv")
    print("✓ bess_tam_bottomup.csv")
    print("✓ bess_sam.csv")
    print("✓ bess_segments.csv")
    print()

    # Key highlights
    print("=" * 80)
    print("KEY MARKET INSIGHTS")
    print("=" * 80)
    tam_2025 = tam_topdown[tam_topdown['Year'] == 2025]['Storage TAM (GWh)'].values[0]
    tam_2030 = tam_topdown[tam_topdown['Year'] == 2030]['Storage TAM (GWh)'].values[0]
    tam_2035 = tam_topdown[tam_topdown['Year'] == 2035]['Storage TAM (GWh)'].values[0]

    print(f"\n2025 Global TAM: {tam_2025:.0f} GWh (${tam_topdown[tam_topdown['Year'] == 2025]['TAM Value ($B)'].values[0]:.0f}B)")
    print(f"2030 Global TAM: {tam_2030:.0f} GWh (${tam_topdown[tam_topdown['Year'] == 2030]['TAM Value ($B)'].values[0]:.0f}B)")
    print(f"2035 Global TAM: {tam_2035:.0f} GWh (${tam_topdown[tam_topdown['Year'] == 2035]['TAM Value ($B)'].values[0]:.0f}B)")

    print(f"\nGrowth: {((tam_2030/tam_2025) - 1)*100:.0f}% expansion (2025→2030)")
    print(f"CAGR 2024-2035: {cagr['GWh CAGR 2024-2035']:.1%}")
    print("\n✓ Market Model Complete")
