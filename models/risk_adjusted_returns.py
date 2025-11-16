"""
Risk-Adjusted Returns Model for Battery Supply Chain Portfolio
Probability-weighted returns, downside risk metrics, and stress testing
"""

import numpy as np
import pandas as pd
from scipy import stats

class RiskAdjustedReturns:
    """Calculate risk-adjusted performance metrics for battery supply chain investments"""

    def __init__(self):
        self.holdings = ['Albemarle', 'CATL', 'Tesla Energy', 'Fluence', 'Lithium Americas']

        # Scenario probabilities
        self.scenario_probs = {
            'Bear': 0.20,
            'Base': 0.50,
            'Bull': 0.25,
            'Black Swan': 0.05
        }

        # Returns by holding by scenario (1-year)
        self.returns_1y = {
            'Bear': np.array([-0.25, -0.10, -0.15, -0.20, -0.65]),
            'Base': np.array([0.12, 0.06, 0.18, 0.10, 0.45]),
            'Bull': np.array([0.60, 0.25, 0.55, 0.45, 2.50]),
            'Black Swan': np.array([0.80, -0.30, 0.40, -0.10, 1.20])  # Geopolitical shock favors US assets
        }

        # Returns by holding by scenario (5-year annualized)
        self.returns_5y = {
            'Bear': np.array([-0.05, 0.02, 0.05, 0.00, -0.15]),
            'Base': np.array([0.15, 0.08, 0.22, 0.14, 0.35]),
            'Bull': np.array([0.35, 0.18, 0.40, 0.30, 0.70]),
            'Black Swan': np.array([0.25, 0.00, 0.30, 0.10, 0.50])
        }

        # Volatilities (annual std dev) by holding
        self.volatilities = np.array([0.45, 0.32, 0.38, 0.40, 0.65])

        # Benchmark (S&P 500)
        self.benchmark_returns = {
            'Bear': -0.15,
            'Base': 0.08,
            'Bull': 0.20,
            'Black Swan': -0.25
        }
        self.benchmark_vol = 0.18

        # Risk-free rate
        self.risk_free_rate = 0.038

    def calculate_expected_returns(self, horizon='1y'):
        """Calculate probability-weighted expected returns"""
        returns_dict = self.returns_1y if horizon == '1y' else self.returns_5y
        expected_returns = np.zeros(len(self.holdings))

        for scenario, prob in self.scenario_probs.items():
            expected_returns += prob * returns_dict[scenario]

        return expected_returns

    def calculate_downside_deviation(self, horizon='1y'):
        """Calculate downside deviation (semi-variance) for each holding"""
        returns_dict = self.returns_1y if horizon == '1y' else self.returns_5y
        downside_devs = []

        for i in range(len(self.holdings)):
            downside_variance = 0
            for scenario, prob in self.scenario_probs.items():
                ret = returns_dict[scenario][i]
                if ret < 0:  # Only consider downside
                    downside_variance += prob * (ret ** 2)

            downside_devs.append(np.sqrt(downside_variance))

        return np.array(downside_devs)

    def calculate_sharpe_ratio(self, horizon='1y'):
        """Calculate Sharpe ratio for each holding"""
        expected_rets = self.calculate_expected_returns(horizon)
        sharpe_ratios = (expected_rets - self.risk_free_rate) / self.volatilities
        return sharpe_ratios

    def calculate_sortino_ratio(self, horizon='1y'):
        """Calculate Sortino ratio (uses downside deviation)"""
        expected_rets = self.calculate_expected_returns(horizon)
        downside_devs = self.calculate_downside_deviation(horizon)

        # Avoid division by zero
        downside_devs = np.where(downside_devs == 0, 0.01, downside_devs)
        sortino_ratios = (expected_rets - self.risk_free_rate) / downside_devs

        return sortino_ratios

    def calculate_cvar(self, confidence=0.95, horizon='1y'):
        """Calculate Conditional Value at Risk (CVaR) - expected loss in worst 5% scenarios"""
        returns_dict = self.returns_1y if horizon == '1y' else self.returns_5y

        # For simplicity, using Bear and Black Swan as tail scenarios
        tail_probs = {'Bear': 0.20, 'Black Swan': 0.05}
        total_tail_prob = sum(tail_probs.values())

        cvar_values = np.zeros(len(self.holdings))
        for scenario in tail_probs:
            weight = tail_probs[scenario] / total_tail_prob
            cvar_values += weight * returns_dict[scenario]

        return cvar_values  # Negative values indicate expected loss

    def stress_test(self):
        """Simulate historical analogs: 2008 financial crisis, 2020 COVID"""
        stress_scenarios = {
            '2008 Financial Crisis Analog': {
                'description': 'Credit freeze, commodity collapse, risk-off',
                'returns': np.array([-0.55, -0.35, -0.60, -0.45, -0.80])  # All down sharply
            },
            '2020 COVID Crash Analog': {
                'description': 'Pandemic demand shock, rapid recovery',
                'returns': np.array([-0.35, -0.25, -0.30, -0.40, -0.50])  # Less severe, quicker rebound
            },
            'Lithium Price Collapse': {
                'description': 'Sustained oversupply, prices <$10k/tonne',
                'returns': np.array([-0.60, 0.05, 0.10, -0.05, -0.85])  # Upstream crushed, midstream/downstream protected
            }
        }

        return stress_scenarios

    def portfolio_metrics(self, weights, horizon='1y'):
        """Calculate portfolio-level risk-adjusted metrics"""
        expected_rets = self.calculate_expected_returns(horizon)
        portfolio_return = np.dot(weights, expected_rets)

        # Simplified portfolio volatility (assuming zero correlation for conservative estimate)
        portfolio_var = np.dot(weights ** 2, self.volatilities ** 2)
        portfolio_vol = np.sqrt(portfolio_var)

        sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol

        # Downside deviation
        downside_devs = self.calculate_downside_deviation(horizon)
        portfolio_downside = np.sqrt(np.dot(weights ** 2, downside_devs ** 2))
        sortino = (portfolio_return - self.risk_free_rate) / portfolio_downside

        return {
            'return': portfolio_return,
            'volatility': portfolio_vol,
            'sharpe': sharpe,
            'sortino': sortino
        }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    model = RiskAdjustedReturns()

    print("=" * 80)
    print("RISK-ADJUSTED RETURNS ANALYSIS")
    print("=" * 80)
    print()

    # Expected returns
    print("1. PROBABILITY-WEIGHTED EXPECTED RETURNS")
    print("-" * 80)
    exp_ret_1y = model.calculate_expected_returns('1y')
    exp_ret_5y = model.calculate_expected_returns('5y')

    returns_df = pd.DataFrame({
        'Holding': model.holdings,
        '1-Year Expected Return': exp_ret_1y,
        '5-Year Expected Return (Ann.)': exp_ret_5y
    })
    print(returns_df.to_string(index=False))
    print()

    # Risk metrics
    print("\n2. RISK METRICS BY HOLDING")
    print("-" * 80)
    sharpe_1y = model.calculate_sharpe_ratio('1y')
    sortino_1y = model.calculate_sortino_ratio('1y')
    cvar_95 = model.calculate_cvar(0.95, '1y')

    risk_df = pd.DataFrame({
        'Holding': model.holdings,
        'Volatility': model.volatilities,
        'Downside Dev': model.calculate_downside_deviation('1y'),
        'Sharpe Ratio': sharpe_1y,
        'Sortino Ratio': sortino_1y,
        'CVaR 95%': cvar_95
    })
    print(risk_df.to_string(index=False))
    print()

    # Scenario analysis
    print("\n3. RETURNS BY SCENARIO (1-Year)")
    print("-" * 80)
    scenario_data = []
    for scenario, prob in model.scenario_probs.items():
        row = {'Scenario': scenario, 'Probability': f"{prob:.0%}"}
        for i, holding in enumerate(model.holdings):
            row[holding] = f"{model.returns_1y[scenario][i]:+.1%}"
        scenario_data.append(row)

    scenario_df = pd.DataFrame(scenario_data)
    print(scenario_df.to_string(index=False))
    print()

    # Stress tests
    print("\n4. STRESS TEST SCENARIOS")
    print("-" * 80)
    stress_scenarios = model.stress_test()

    for scenario_name, scenario_data in stress_scenarios.items():
        print(f"\n{scenario_name}:")
        print(f"  {scenario_data['description']}")
        for i, holding in enumerate(model.holdings):
            print(f"    {holding}: {scenario_data['returns'][i]:+.1%}")

    print()

    # Portfolio-level metrics
    print("\n5. PORTFOLIO-LEVEL RISK-ADJUSTED RETURNS")
    print("-" * 80)

    # Example portfolios
    portfolios = {
        'Equal Weight': np.array([0.20, 0.20, 0.20, 0.20, 0.20]),
        'Growth Focus': np.array([0.15, 0.15, 0.35, 0.20, 0.15]),
        'Conservative': np.array([0.30, 0.40, 0.15, 0.10, 0.05])
    }

    portfolio_results = []
    for port_name, weights in portfolios.items():
        metrics_1y = model.portfolio_metrics(weights, '1y')
        metrics_5y = model.portfolio_metrics(weights, '5y')

        portfolio_results.append({
            'Portfolio': port_name,
            '1Y Return': metrics_1y['return'],
            '1Y Volatility': metrics_1y['volatility'],
            '1Y Sharpe': metrics_1y['sharpe'],
            '5Y Return (Ann.)': metrics_5y['return']
        })

    portfolio_df = pd.DataFrame(portfolio_results)
    print(portfolio_df.to_string(index=False))
    print()

    # Export results
    print("\n6. EXPORTING RESULTS")
    print("-" * 80)
    returns_df.to_csv('/home/user/TDITG/models/expected_returns.csv', index=False)
    risk_df.to_csv('/home/user/TDITG/models/risk_metrics.csv', index=False)
    scenario_df.to_csv('/home/user/TDITG/models/scenario_returns.csv', index=False)
    portfolio_df.to_csv('/home/user/TDITG/models/portfolio_risk_adjusted.csv', index=False)

    print("✓ expected_returns.csv")
    print("✓ risk_metrics.csv")
    print("✓ scenario_returns.csv")
    print("✓ portfolio_risk_adjusted.csv")
    print()

    print("=" * 80)
    print("INVESTMENT DECISION FRAMEWORK")
    print("=" * 80)

    best_sharpe_idx = np.argmax(sharpe_1y)
    best_sortino_idx = np.argmax(sortino_1y)

    print(f"\nHighest Sharpe Ratio: {model.holdings[best_sharpe_idx]} ({sharpe_1y[best_sharpe_idx]:.2f})")
    print(f"Highest Sortino Ratio: {model.holdings[best_sortino_idx]} ({sortino_1y[best_sortino_idx]:.2f})")

    print(f"\nProbability-Weighted 1-Year Portfolio Return (Equal Weight): {np.mean(exp_ret_1y):.1%}")
    print(f"Benchmark (S&P 500) Expected: {sum([model.scenario_probs[s] * model.benchmark_returns[s] for s in model.scenario_probs]):.1%}")

    print("\n✓ Risk-Adjusted Returns Analysis Complete")
