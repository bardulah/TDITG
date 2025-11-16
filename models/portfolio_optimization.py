"""
Portfolio Optimization Model for Battery Supply Chain Investments
Modern Portfolio Theory with efficient frontier, risk parity, and scenario-based allocation
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize

class BatteryPortfolioOptimizer:
    """Portfolio optimization for 5 battery supply chain holdings"""

    def __init__(self):
        # Holdings
        self.holdings = ['Albemarle', 'CATL', 'Tesla Energy', 'Fluence', 'Lithium Americas']

        # Expected returns (annual) - Base case scenario
        self.expected_returns = np.array([0.12, 0.06, 0.18, 0.10, 0.45])  # Albemarle, CATL, Tesla, Fluence, LAC

        # Volatility (annual std deviation)
        self.volatilities = np.array([0.45, 0.32, 0.38, 0.40, 0.65])

        # Correlation matrix (based on business model similarities and commodity exposure)
        self.correlation_matrix = np.array([
            [1.00, 0.55, 0.50, 0.45, 0.75],  # Albemarle: high correlation with LAC (both upstream lithium)
            [0.55, 1.00, 0.60, 0.55, 0.40],  # CATL: moderate correlation across chain
            [0.50, 0.60, 1.00, 0.70, 0.35],  # Tesla Energy: high correlation with Fluence (both downstream)
            [0.45, 0.55, 0.70, 1.00, 0.30],  # Fluence: highest with Tesla (direct competitors)
            [0.75, 0.40, 0.35, 0.30, 1.00]   # LAC: highest with Albemarle (both lithium producers)
        ])

        # Covariance matrix
        self.cov_matrix = self.correlation_to_covariance(
            self.correlation_matrix, self.volatilities
        )

        # Risk-free rate
        self.risk_free_rate = 0.038

        # Constraints
        self.max_single_position = 0.40  # No more than 40% in any single holding
        self.min_position = 0.05  # Minimum 5% per holding for diversification

    @staticmethod
    def correlation_to_covariance(corr_matrix, volatilities):
        """Convert correlation matrix to covariance matrix"""
        n = len(volatilities)
        cov_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                cov_matrix[i, j] = corr_matrix[i, j] * volatilities[i] * volatilities[j]
        return cov_matrix

    def portfolio_stats(self, weights):
        """Calculate portfolio return, volatility, and Sharpe ratio"""
        port_return = np.dot(weights, self.expected_returns)
        port_vol = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        sharpe = (port_return - self.risk_free_rate) / port_vol
        return port_return, port_vol, sharpe

    def negative_sharpe(self, weights):
        """Objective function to minimize (negative Sharpe ratio)"""
        return -self.portfolio_stats(weights)[2]

    def portfolio_volatility(self, weights):
        """Objective function for minimum variance portfolio"""
        return self.portfolio_stats(weights)[1]

    def optimize_max_sharpe(self):
        """Find portfolio with maximum Sharpe ratio"""
        n = len(self.holdings)

        # Constraints
        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
        )

        # Bounds
        bounds = tuple((self.min_position, self.max_single_position) for _ in range(n))

        # Initial guess (equal weight)
        init_guess = np.array([1/n] * n)

        # Optimize
        result = minimize(
            self.negative_sharpe,
            init_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        return result.x

    def optimize_min_variance(self):
        """Find minimum variance portfolio"""
        n = len(self.holdings)

        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        )

        bounds = tuple((self.min_position, self.max_single_position) for _ in range(n))
        init_guess = np.array([1/n] * n)

        result = minimize(
            self.portfolio_volatility,
            init_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        return result.x

    def risk_parity_allocation(self):
        """Calculate risk parity (equal risk contribution) allocation"""
        # Inverse volatility weighting as approximation
        inv_vol = 1 / self.volatilities
        weights = inv_vol / np.sum(inv_vol)

        # Normalize to respect constraints
        weights = np.clip(weights, self.min_position, self.max_single_position)
        weights = weights / np.sum(weights)

        return weights

    def efficient_frontier(self, n_points=50):
        """Generate efficient frontier"""
        min_var_weights = self.optimize_min_variance()
        max_sharpe_weights = self.optimize_max_sharpe()

        min_return, _, _ = self.portfolio_stats(min_var_weights)
        max_return, _, _ = self.portfolio_stats(max_sharpe_weights)

        target_returns = np.linspace(min_return, max_return * 1.1, n_points)

        frontier_vols = []
        frontier_returns = []
        frontier_sharpes = []

        for target in target_returns:
            constraints = (
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'eq', 'fun': lambda x: np.dot(x, self.expected_returns) - target}
            )

            bounds = tuple((self.min_position, self.max_single_position) for _ in range(len(self.holdings)))
            init_guess = np.array([1/len(self.holdings)] * len(self.holdings))

            result = minimize(
                self.portfolio_volatility,
                init_guess,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )

            if result.success:
                ret, vol, sharpe = self.portfolio_stats(result.x)
                frontier_returns.append(ret)
                frontier_vols.append(vol)
                frontier_sharpes.append(sharpe)

        return np.array(frontier_returns), np.array(frontier_vols), np.array(frontier_sharpes)

    def scenario_allocation(self, scenario='base'):
        """Recommend allocation based on market scenario"""
        if scenario == 'bull':  # High lithium prices, accelerating adoption
            # Overweight upstream (Albemarle, LAC) and growth (Tesla)
            weights = np.array([0.30, 0.15, 0.30, 0.10, 0.15])  # Albemarle, CATL, Tesla, Fluence, LAC
        elif scenario == 'bear':  # Oversupply, margin compression
            # Prefer quality with scale (CATL, Albemarle), underweight development (LAC)
            weights = np.array([0.30, 0.40, 0.15, 0.10, 0.05])
        else:  # Base case
            # Balanced exposure across value chain
            weights = np.array([0.25, 0.25, 0.25, 0.15, 0.10])

        return weights

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    optimizer = BatteryPortfolioOptimizer()

    print("=" * 80)
    print("BATTERY SUPPLY CHAIN - PORTFOLIO OPTIMIZATION")
    print("=" * 80)
    print()

    # Equal weight benchmark
    equal_weights = np.array([0.20, 0.20, 0.20, 0.20, 0.20])
    eq_ret, eq_vol, eq_sharpe = optimizer.portfolio_stats(equal_weights)

    print("0. BENCHMARK: EQUAL-WEIGHT PORTFOLIO")
    print("-" * 80)
    for i, holding in enumerate(optimizer.holdings):
        print(f"{holding}: {equal_weights[i]:.1%}")
    print(f"\nExpected Return: {eq_ret:.2%}")
    print(f"Volatility: {eq_vol:.2%}")
    print(f"Sharpe Ratio: {eq_sharpe:.2f}")
    print()

    # Maximum Sharpe ratio portfolio
    print("\n1. MAXIMUM SHARPE RATIO PORTFOLIO")
    print("-" * 80)
    max_sharpe_weights = optimizer.optimize_max_sharpe()
    ms_ret, ms_vol, ms_sharpe = optimizer.portfolio_stats(max_sharpe_weights)

    for i, holding in enumerate(optimizer.holdings):
        print(f"{holding}: {max_sharpe_weights[i]:.1%}")
    print(f"\nExpected Return: {ms_ret:.2%}")
    print(f"Volatility: {ms_vol:.2%}")
    print(f"Sharpe Ratio: {ms_sharpe:.2f}")
    print()

    # Minimum variance portfolio
    print("\n2. MINIMUM VARIANCE PORTFOLIO")
    print("-" * 80)
    min_var_weights = optimizer.optimize_min_variance()
    mv_ret, mv_vol, mv_sharpe = optimizer.portfolio_stats(min_var_weights)

    for i, holding in enumerate(optimizer.holdings):
        print(f"{holding}: {min_var_weights[i]:.1%}")
    print(f"\nExpected Return: {mv_ret:.2%}")
    print(f"Volatility: {mv_vol:.2%}")
    print(f"Sharpe Ratio: {mv_sharpe:.2f}")
    print()

    # Risk parity
    print("\n3. RISK PARITY ALLOCATION")
    print("-" * 80)
    rp_weights = optimizer.risk_parity_allocation()
    rp_ret, rp_vol, rp_sharpe = optimizer.portfolio_stats(rp_weights)

    for i, holding in enumerate(optimizer.holdings):
        print(f"{holding}: {rp_weights[i]:.1%}")
    print(f"\nExpected Return: {rp_ret:.2%}")
    print(f"Volatility: {rp_vol:.2%}")
    print(f"Sharpe Ratio: {rp_sharpe:.2f}")
    print()

    # Scenario-based allocations
    print("\n4. SCENARIO-BASED ALLOCATIONS")
    print("-" * 80)

    for scenario in ['bear', 'base', 'bull']:
        print(f"\n{scenario.upper()} Scenario:")
        sc_weights = optimizer.scenario_allocation(scenario)
        sc_ret, sc_vol, sc_sharpe = optimizer.portfolio_stats(sc_weights)

        for i, holding in enumerate(optimizer.holdings):
            print(f"  {holding}: {sc_weights[i]:.1%}")
        print(f"  Expected Return: {sc_ret:.2%}, Volatility: {sc_vol:.2%}, Sharpe: {sc_sharpe:.2f}")

    print()

    # Export results
    print("\n5. EXPORTING RESULTS")
    print("-" * 80)

    # Compile allocations
    allocations_df = pd.DataFrame({
        'Holding': optimizer.holdings,
        'Equal Weight': equal_weights,
        'Max Sharpe': max_sharpe_weights,
        'Min Variance': min_var_weights,
        'Risk Parity': rp_weights,
        'Bear Scenario': optimizer.scenario_allocation('bear'),
        'Base Scenario': optimizer.scenario_allocation('base'),
        'Bull Scenario': optimizer.scenario_allocation('bull')
    })
    allocations_df.to_csv('/home/user/TDITG/models/portfolio_allocations.csv', index=False)

    # Portfolio statistics
    stats_df = pd.DataFrame({
        'Portfolio': ['Equal Weight', 'Max Sharpe', 'Min Variance', 'Risk Parity'],
        'Expected Return': [eq_ret, ms_ret, mv_ret, rp_ret],
        'Volatility': [eq_vol, ms_vol, mv_vol, rp_vol],
        'Sharpe Ratio': [eq_sharpe, ms_sharpe, mv_sharpe, rp_sharpe]
    })
    stats_df.to_csv('/home/user/TDITG/models/portfolio_statistics.csv', index=False)

    print("✓ portfolio_allocations.csv")
    print("✓ portfolio_statistics.csv")
    print()

    print("=" * 80)
    print("RECOMMENDED ALLOCATION")
    print("=" * 80)
    print("\nFor balanced risk-adjusted returns, recommend MAX SHARPE portfolio:")
    for i, holding in enumerate(optimizer.holdings):
        print(f"  {holding}: {max_sharpe_weights[i]:.1%}")
    print(f"\n  Target 1-Year Return: {ms_ret:.1%}")
    print(f"  Expected Volatility: {ms_vol:.1%}")
    print(f"  Sharpe Ratio: {ms_sharpe:.2f}")
    print("\n✓ Portfolio Optimization Complete")
