"""
Portfolio Optimization Model for Sub-$5 Multi-Sector Portfolio
Calculates optimal allocations, risk metrics, and expected returns
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

class Sub5PortfolioOptimizer:
    """Optimizes portfolio allocation for sub-$5 stocks"""

    def __init__(self):
        # Holdings with current metrics
        self.holdings = {
            'BBAI': {
                'name': 'BigBear.ai',
                'price': 3.87,
                'sector': 'AI/Defense',
                'market_cap_M': 900,
                'expected_return': 0.25,  # 25% annual
                'volatility': 0.75,  # 75% annual std dev
                'beta': 1.8
            },
            'DNN': {
                'name': 'Denison Mines',
                'price': 2.39,
                'sector': 'Uranium',
                'market_cap_M': 2150,
                'expected_return': 0.40,  # 40% annual (uranium tailwinds)
                'volatility': 0.65,
                'beta': 1.5
            },
            'URG': {
                'name': 'Ur-Energy',
                'price': 1.21,
                'sector': 'Uranium',
                'market_cap_M': 459,
                'expected_return': 0.55,  # 55% annual (105% analyst target)
                'volatility': 0.80,
                'beta': 1.7
            },
            'RR': {
                'name': 'Richtech Robotics',
                'price': 2.37,
                'sector': 'Robotics',
                'market_cap_M': 150,
                'expected_return': 0.35,  # 35% annual
                'volatility': 0.90,  # Very high volatility
                'beta': 2.0
            },
            'SFET': {
                'name': 'Safe-T Group',
                'price': 1.24,
                'sector': 'Cybersecurity',
                'market_cap_M': 4,
                'expected_return': 0.30,  # 30% annual
                'volatility': 1.20,  # Extreme volatility (micro-cap)
                'beta': 1.5
            }
        }

        # Correlation matrix (estimated based on sector relationships)
        self.correlation_matrix = np.array([
            # BBAI   DNN    URG    RR    SFET
            [1.00,  0.20,  0.20,  0.35, 0.40],  # BBAI - AI/Defense
            [0.20,  1.00,  0.85,  0.15, 0.10],  # DNN - Uranium
            [0.20,  0.85,  1.00,  0.15, 0.10],  # URG - Uranium
            [0.35,  0.15,  0.15,  1.00, 0.30],  # RR - Robotics
            [0.40,  0.10,  0.10,  0.30, 1.00],  # SFET - Cybersecurity
        ])

        self.tickers = list(self.holdings.keys())

    def get_expected_returns(self) -> np.array:
        """Get expected returns vector"""
        return np.array([self.holdings[t]['expected_return'] for t in self.tickers])

    def get_volatilities(self) -> np.array:
        """Get volatility vector"""
        return np.array([self.holdings[t]['volatility'] for t in self.tickers])

    def get_covariance_matrix(self) -> np.array:
        """Calculate covariance matrix from correlations and volatilities"""
        vols = self.get_volatilities()
        cov = np.outer(vols, vols) * self.correlation_matrix
        return cov

    def portfolio_return(self, weights: np.array) -> float:
        """Calculate expected portfolio return"""
        returns = self.get_expected_returns()
        return np.dot(weights, returns)

    def portfolio_volatility(self, weights: np.array) -> float:
        """Calculate portfolio volatility"""
        cov = self.get_covariance_matrix()
        variance = np.dot(weights.T, np.dot(cov, weights))
        return np.sqrt(variance)

    def portfolio_sharpe(self, weights: np.array, risk_free: float = 0.04) -> float:
        """Calculate Sharpe ratio"""
        ret = self.portfolio_return(weights)
        vol = self.portfolio_volatility(weights)
        return (ret - risk_free) / vol

    def equal_weight_portfolio(self) -> Dict:
        """Calculate equal-weight portfolio metrics"""
        weights = np.array([0.20, 0.20, 0.20, 0.20, 0.20])

        return {
            'name': 'Equal Weight',
            'weights': dict(zip(self.tickers, weights)),
            'expected_return': self.portfolio_return(weights),
            'volatility': self.portfolio_volatility(weights),
            'sharpe_ratio': self.portfolio_sharpe(weights)
        }

    def conviction_weighted_portfolio(self) -> Dict:
        """Conviction-based allocation (overweight uranium/AI)"""
        weights = np.array([0.25, 0.30, 0.25, 0.12, 0.08])

        return {
            'name': 'Conviction Weighted',
            'weights': dict(zip(self.tickers, weights)),
            'expected_return': self.portfolio_return(weights),
            'volatility': self.portfolio_volatility(weights),
            'sharpe_ratio': self.portfolio_sharpe(weights)
        }

    def risk_parity_portfolio(self) -> Dict:
        """Risk parity allocation (equal risk contribution)"""
        vols = self.get_volatilities()

        # Inverse volatility weighting (simplified risk parity)
        inv_vols = 1 / vols
        weights = inv_vols / np.sum(inv_vols)

        return {
            'name': 'Risk Parity',
            'weights': dict(zip(self.tickers, weights)),
            'expected_return': self.portfolio_return(weights),
            'volatility': self.portfolio_volatility(weights),
            'sharpe_ratio': self.portfolio_sharpe(weights)
        }

    def max_sharpe_portfolio(self, num_simulations: int = 10000) -> Dict:
        """Find maximum Sharpe ratio portfolio via Monte Carlo"""
        best_sharpe = -np.inf
        best_weights = None

        for _ in range(num_simulations):
            # Generate random weights
            weights = np.random.random(5)
            weights = weights / np.sum(weights)

            sharpe = self.portfolio_sharpe(weights)
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_weights = weights

        return {
            'name': 'Max Sharpe',
            'weights': dict(zip(self.tickers, best_weights)),
            'expected_return': self.portfolio_return(best_weights),
            'volatility': self.portfolio_volatility(best_weights),
            'sharpe_ratio': best_sharpe
        }

    def scenario_analysis(self) -> pd.DataFrame:
        """Run scenario analysis across market conditions"""

        scenarios = {
            'Base Case': {
                'market_return': 0.10,
                'uranium_premium': 0.0,
                'ai_premium': 0.0,
                'probability': 0.50
            },
            'Uranium Bull': {
                'market_return': 0.08,
                'uranium_premium': 0.30,  # +30% to uranium names
                'ai_premium': 0.0,
                'probability': 0.20
            },
            'AI Defense Surge': {
                'market_return': 0.12,
                'uranium_premium': 0.0,
                'ai_premium': 0.25,  # +25% to AI/defense
                'probability': 0.15
            },
            'Risk-Off (Bear)': {
                'market_return': -0.15,
                'uranium_premium': -0.20,
                'ai_premium': -0.25,
                'probability': 0.10
            },
            'Super Bull': {
                'market_return': 0.20,
                'uranium_premium': 0.40,
                'ai_premium': 0.35,
                'probability': 0.05
            }
        }

        # Use conviction-weighted portfolio
        weights = np.array([0.25, 0.30, 0.25, 0.12, 0.08])

        results = []
        for scenario_name, params in scenarios.items():
            # Adjust returns based on scenario
            adjusted_returns = []
            for i, ticker in enumerate(self.tickers):
                base_return = self.holdings[ticker]['expected_return']

                if ticker in ['DNN', 'URG']:
                    adj = base_return + params['uranium_premium']
                elif ticker in ['BBAI', 'SFET']:
                    adj = base_return + params['ai_premium']
                else:
                    adj = base_return + params['market_return'] - 0.10  # RR follows market

                adjusted_returns.append(adj)

            adjusted_returns = np.array(adjusted_returns)
            scenario_return = np.dot(weights, adjusted_returns)

            results.append({
                'Scenario': scenario_name,
                'Probability': params['probability'],
                'Portfolio_Return': scenario_return,
                'BBAI_Return': adjusted_returns[0],
                'DNN_Return': adjusted_returns[1],
                'URG_Return': adjusted_returns[2],
                'RR_Return': adjusted_returns[3],
                'SFET_Return': adjusted_returns[4]
            })

        return pd.DataFrame(results)

    def calculate_var_cvar(self, weights: np.array, confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate Value at Risk and Conditional VaR"""

        # Monte Carlo simulation
        n_sims = 10000
        cov = self.get_covariance_matrix()
        returns = self.get_expected_returns()

        # Simulate returns
        simulated = np.random.multivariate_normal(returns, cov, n_sims)
        portfolio_returns = np.dot(simulated, weights)

        # Sort returns
        sorted_returns = np.sort(portfolio_returns)

        # VaR at confidence level
        var_index = int((1 - confidence) * n_sims)
        var = -sorted_returns[var_index]

        # CVaR (expected shortfall)
        cvar = -np.mean(sorted_returns[:var_index])

        return var, cvar

    def generate_report(self) -> str:
        """Generate comprehensive portfolio analysis report"""

        report = []
        report.append("=" * 60)
        report.append("SUB-$5 PORTFOLIO OPTIMIZATION REPORT")
        report.append("=" * 60)

        # Holdings summary
        report.append("\n--- HOLDINGS SUMMARY ---")
        for ticker, data in self.holdings.items():
            report.append(f"\n{ticker} - {data['name']}")
            report.append(f"  Price: ${data['price']:.2f}")
            report.append(f"  Sector: {data['sector']}")
            report.append(f"  Expected Return: {data['expected_return']*100:.0f}%")
            report.append(f"  Volatility: {data['volatility']*100:.0f}%")

        # Portfolio strategies
        report.append("\n--- PORTFOLIO STRATEGIES ---")

        strategies = [
            self.equal_weight_portfolio(),
            self.conviction_weighted_portfolio(),
            self.risk_parity_portfolio(),
            self.max_sharpe_portfolio()
        ]

        for strat in strategies:
            report.append(f"\n{strat['name']}:")
            report.append(f"  Expected Return: {strat['expected_return']*100:.1f}%")
            report.append(f"  Volatility: {strat['volatility']*100:.1f}%")
            report.append(f"  Sharpe Ratio: {strat['sharpe_ratio']:.2f}")
            report.append("  Weights:")
            for t, w in strat['weights'].items():
                report.append(f"    {t}: {w*100:.1f}%")

        # Scenario analysis
        report.append("\n--- SCENARIO ANALYSIS ---")
        scenarios = self.scenario_analysis()
        report.append(scenarios.to_string(index=False))

        # Probability-weighted return
        weighted_return = sum(
            row['Portfolio_Return'] * row['Probability']
            for _, row in scenarios.iterrows()
        )
        report.append(f"\nProbability-Weighted Return: {weighted_return*100:.1f}%")

        # Risk metrics
        report.append("\n--- RISK METRICS ---")
        weights = np.array([0.25, 0.30, 0.25, 0.12, 0.08])
        var, cvar = self.calculate_var_cvar(weights)
        report.append(f"95% VaR (1-year): {var*100:.1f}%")
        report.append(f"95% CVaR (Expected Shortfall): {cvar*100:.1f}%")

        return "\n".join(report)

def run_portfolio_optimization():
    """Run portfolio optimization and export results"""

    optimizer = Sub5PortfolioOptimizer()

    # Generate and print report
    report = optimizer.generate_report()
    print(report)

    # Export scenario analysis
    scenarios = optimizer.scenario_analysis()
    scenarios.to_csv('/home/user/TDITG/sub5_models/portfolio_scenarios.csv', index=False)

    # Export portfolio strategies
    strategies = [
        optimizer.equal_weight_portfolio(),
        optimizer.conviction_weighted_portfolio(),
        optimizer.risk_parity_portfolio(),
        optimizer.max_sharpe_portfolio()
    ]

    strat_df = pd.DataFrame(strategies)
    strat_df.to_csv('/home/user/TDITG/sub5_models/portfolio_strategies.csv', index=False)

    print("\n[Results exported to CSV files]")

    return optimizer

if __name__ == "__main__":
    optimizer = run_portfolio_optimization()
