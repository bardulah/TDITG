"""
Commodity Price Scenario Model for Battery Raw Materials
Stochastic modeling with mean-reversion, supply-demand balance, and scenario analysis
"""

import numpy as np
import pandas as pd
from scipy import stats

class CommodityPriceModel:
    """Stochastic price model for lithium and battery metals"""

    def __init__(self):
        # Base prices (2024 average, $/tonne)
        self.base_prices = {
            'Lithium Carbonate': 14000,
            'Lithium Hydroxide': 15000,
            'Cobalt': 28000,
            'Nickel (Class 1)': 18000,
            'Natural Graphite': 800
        }

        # Long-term mean reversion prices (equilibrium)
        self.mean_reversion_prices = {
            'Lithium Carbonate': 22000,
            'Lithium Hydroxide': 23500,
            'Cobalt': 35000,
            'Nickel (Class 1)': 22000,
            'Natural Graphite': 1200
        }

        # Mean reversion speed (higher = faster reversion)
        self.reversion_speed = 0.25

        # Volatility (annual std deviation)
        self.volatilities = {
            'Lithium Carbonate': 0.35,
            'Lithium Hydroxide': 0.33,
            'Cobalt': 0.28,
            'Nickel (Class 1)': 0.25,
            'Natural Graphite': 0.22
        }

        # Correlation matrix (commodities tend to move together)
        self.correlation_matrix = np.array([
            [1.00, 0.95, 0.60, 0.65, 0.55],  # Li2CO3
            [0.95, 1.00, 0.58, 0.63, 0.53],  # LiOH
            [0.60, 0.58, 1.00, 0.75, 0.50],  # Cobalt
            [0.65, 0.63, 0.75, 1.00, 0.55],  # Nickel
            [0.55, 0.53, 0.50, 0.55, 1.00]   # Graphite
        ])

        self.commodities = list(self.base_prices.keys())

    def generate_price_paths(self, years=12, n_paths=1000):
        """Generate correlated price paths using geometric Brownian motion with mean reversion"""
        np.random.seed(42)
        n_years = years
        dt = 1  # Annual time step

        # Initialize price matrix: [paths, years, commodities]
        prices = np.zeros((n_paths, n_years, len(self.commodities)))

        # Set initial prices
        for i, commodity in enumerate(self.commodities):
            prices[:, 0, i] = self.base_prices[commodity]

        # Generate correlated random shocks
        cholesky = np.linalg.cholesky(self.correlation_matrix)

        for t in range(1, n_years):
            # Generate independent standard normal random variables
            z = np.random.standard_normal((n_paths, len(self.commodities)))

            # Apply correlation
            correlated_z = z @ cholesky.T

            # Update prices with mean reversion
            for i, commodity in enumerate(self.commodities):
                current_price = prices[:, t-1, i]
                mean_price = self.mean_reversion_prices[commodity]
                vol = self.volatilities[commodity]
                kappa = self.reversion_speed

                # Mean reversion drift
                drift = kappa * (np.log(mean_price) - np.log(current_price))

                # Price update
                prices[:, t, i] = current_price * np.exp(
                    drift * dt - 0.5 * vol**2 * dt + vol * np.sqrt(dt) * correlated_z[:, i]
                )

        return prices

    def scenario_deterministic(self):
        """Generate bear/base/bull deterministic scenarios"""
        years = list(range(2024, 2036))
        scenarios = {}

        # Bear case: Oversupply, demand slowdown
        bear_growth = -0.05  # -5% annual from current depressed levels
        scenarios['Bear'] = {}
        for commodity in self.commodities:
            prices = []
            price = self.base_prices[commodity]
            for _ in years:
                prices.append(price)
                price *= (1 + bear_growth)
            scenarios['Bear'][commodity] = prices

        # Base case: Balanced market with moderate deficit
        scenarios['Base'] = {}
        for commodity in self.commodities:
            mean_price = self.mean_reversion_prices[commodity]
            current_price = self.base_prices[commodity]
            # Gradual convergence to mean over 6 years, then stable
            prices = []
            for i, year in enumerate(years):
                if i < 6:
                    weight = i / 6
                    price = current_price * (1 - weight) + mean_price * weight
                else:
                    price = mean_price
                prices.append(price)
            scenarios['Base'][commodity] = prices

        # Bull case: Supply constraints, accelerated demand
        scenarios['Bull'] = {}
        for commodity in self.commodities:
            mean_price = self.mean_reversion_prices[commodity]
            # Overshoot mean by 40% due to tightness
            peak_price = mean_price * 1.40
            current_price = self.base_prices[commodity]
            prices = []
            for i, year in enumerate(years):
                if i < 4:  # Rapid rise to peak
                    weight = i / 4
                    price = current_price * (1 - weight) + peak_price * weight
                elif i < 8:  # Gradual normalization
                    weight = (i - 4) / 4
                    price = peak_price * (1 - weight) + mean_price * weight
                else:  # Stable at mean
                    price = mean_price
                prices.append(price)
            scenarios['Bull'][commodity] = prices

        # Convert to DataFrame
        scenario_dfs = {}
        for scenario_name, scenario_data in scenarios.items():
            df = pd.DataFrame(scenario_data, index=years)
            df.index.name = 'Year'
            scenario_dfs[scenario_name] = df

        return scenario_dfs

    def monte_carlo_statistics(self, price_paths):
        """Calculate statistics from Monte Carlo price paths"""
        # price_paths shape: [paths, years, commodities]
        years = list(range(2024, 2024 + price_paths.shape[1]))

        results = {}
        for i, commodity in enumerate(self.commodities):
            commodity_prices = price_paths[:, :, i]  # All paths for this commodity

            stats_data = []
            for year_idx, year in enumerate(years):
                year_prices = commodity_prices[:, year_idx]

                stats_data.append({
                    'Year': year,
                    'P10': np.percentile(year_prices, 10),
                    'P25': np.percentile(year_prices, 25),
                    'P50': np.percentile(year_prices, 50),
                    'P75': np.percentile(year_prices, 75),
                    'P90': np.percentile(year_prices, 90),
                    'Mean': np.mean(year_prices),
                    'Std Dev': np.std(year_prices)
                })

            results[commodity] = pd.DataFrame(stats_data)

        return results

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    model = CommodityPriceModel()

    print("=" * 80)
    print("BATTERY METALS - COMMODITY PRICE SCENARIO MODEL")
    print("=" * 80)
    print()

    # Deterministic scenarios
    print("1. DETERMINISTIC PRICE SCENARIOS (Bear/Base/Bull)")
    print("-" * 80)
    scenarios = model.scenario_deterministic()

    for scenario_name, scenario_df in scenarios.items():
        print(f"\n{scenario_name} Case:")
        # Display subset of years
        display_years = [2024, 2027, 2030, 2035]
        display_df = scenario_df.loc[display_years].round(0)
        print(display_df.to_string())

    print()

    # Monte Carlo simulation
    print("\n2. MONTE CARLO SIMULATION (1,000 paths, 12 years)")
    print("-" * 80)
    price_paths = model.generate_price_paths(years=12, n_paths=1000)
    mc_stats = model.monte_carlo_statistics(price_paths)

    # Display lithium carbonate statistics as example
    print("\nLithium Carbonate - Price Distribution ($/tonne):")
    print(mc_stats['Lithium Carbonate'].to_string(index=False))
    print()

    # Export results
    print("\n3. EXPORTING RESULTS")
    print("-" * 80)

    # Export scenarios
    for scenario_name, scenario_df in scenarios.items():
        filename = f"/home/user/TDITG/models/commodity_scenario_{scenario_name.lower()}.csv"
        scenario_df.to_csv(filename)
        print(f"✓ commodity_scenario_{scenario_name.lower()}.csv")

    # Export Monte Carlo stats
    for commodity, stats_df in mc_stats.items():
        filename = f"/home/user/TDITG/models/mc_{commodity.replace(' ', '_').lower()}.csv"
        stats_df.to_csv(filename, index=False)
        print(f"✓ mc_{commodity.replace(' ', '_').lower()}.csv")

    print()

    # Investment insights
    print("=" * 80)
    print("COMMODITY OUTLOOK SUMMARY")
    print("=" * 80)

    print("\nLithium Carbonate Price Forecasts ($/tonne):")
    print(f"  Bear 2030: ${scenarios['Bear']['Lithium Carbonate'][6]:.0f}")
    print(f"  Base 2030: ${scenarios['Base']['Lithium Carbonate'][6]:.0f}")
    print(f"  Bull 2030: ${scenarios['Bull']['Lithium Carbonate'][6]:.0f}")

    print(f"\n  Monte Carlo P50 (2030): ${mc_stats['Lithium Carbonate'][mc_stats['Lithium Carbonate']['Year'] == 2030]['P50'].values[0]:.0f}")
    print(f"  Monte Carlo Range (P10-P90): ${mc_stats['Lithium Carbonate'][mc_stats['Lithium Carbonate']['Year'] == 2030]['P10'].values[0]:.0f} - ${mc_stats['Lithium Carbonate'][mc_stats['Lithium Carbonate']['Year'] == 2030]['P90'].values[0]:.0f}")

    print("\nInvestment Implications:")
    print("  • Base case assumes gradual supply-demand rebalancing by 2027-2028")
    print("  • High volatility (35% annual) suggests option value in lithium exposure")
    print("  • Correlation with other battery metals (0.6-0.7) implies portfolio diversification benefits")
    print("\n✓ Commodity Model Complete")
