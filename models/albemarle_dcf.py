"""
Albemarle Corporation (ALB) - Discounted Cash Flow Valuation Model
Comprehensive DCF with scenario analysis, Monte Carlo simulation, and sensitivity tables
"""

import numpy as np
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# MODEL ASSUMPTIONS
# ============================================================================

class AlbemarleDCF:
    """
    Comprehensive DCF model for Albemarle Corporation
    Incorporates lithium production volumes, pricing scenarios, cost structure,
    and capital allocation
    """

    def __init__(self, scenario='base'):
        """
        Initialize model with scenario-specific assumptions

        Parameters:
        -----------
        scenario : str
            One of 'bear', 'base', 'bull'
        """
        self.scenario = scenario
        self.years = list(range(2025, 2035))  # 10-year explicit forecast

        # Lithium price assumptions by scenario ($/tonne LCE)
        self.price_assumptions = {
            'bear': {
                2025: 14000, 2026: 13000, 2027: 14500, 2028: 15000, 2029: 15500,
                2030: 16000, 2031: 16500, 2032: 17000, 2033: 17000, 2034: 17000
            },
            'base': {
                2025: 16000, 2026: 17000, 2027: 19000, 2028: 21000, 2029: 22000,
                2030: 23000, 2031: 23500, 2032: 24000, 2033: 24000, 2034: 24000
            },
            'bull': {
                2025: 20000, 2026: 24000, 2027: 28000, 2028: 30000, 2029: 32000,
                2030: 34000, 2031: 35000, 2032: 35000, 2033: 34000, 2034: 33000
            }
        }

        # Production volume assumptions (tonnes LCE)
        self.production_volumes = {
            2025: 220000, 2026: 245000, 2027: 270000, 2028: 290000, 2029: 305000,
            2030: 320000, 2031: 330000, 2032: 340000, 2033: 345000, 2034: 350000
        }

        # Cash cost per tonne by year (incorporating scale efficiencies)
        self.cash_costs = {
            2025: 9500, 2026: 9200, 2027: 8900, 2028: 8600, 2029: 8400,
            2030: 8200, 2031: 8100, 2032: 8000, 2033: 8000, 2034: 8000
        }

        # Non-lithium business (Bromine/Specialties) - assumes stable
        self.specialties_revenue = 2500  # $M per year
        self.specialties_ebitda_margin = 0.25

        # Tax rate by jurisdiction (blended)
        self.tax_rate = 0.24

        # D&A as % of PP&E
        self.depreciation_rate = 0.08

        # SG&A (relatively fixed)
        self.sga_fixed = 600  # $M per year

        # R&D spending
        self.rd_pct_revenue = 0.03

        # Capex schedule ($M)
        self.capex_schedule = {
            2025: 1200, 2026: 1400, 2027: 1600, 2028: 1400, 2029: 1200,
            2030: 1000, 2031: 900, 2032: 850, 2033: 850, 2034: 850
        }

        # Working capital as % of revenue
        self.wc_pct_revenue = 0.15

        # Terminal assumptions
        self.terminal_growth_rate = 0.02
        self.terminal_margin = 0.20  # Terminal EBITDA margin

        # WACC components
        self.risk_free_rate = 0.038  # 10-year Treasury
        self.equity_risk_premium = 0.065
        self.beta = 1.45  # Albemarle beta
        self.cost_of_debt = 0.055
        self.tax_shield = self.tax_rate
        self.target_debt_ratio = 0.25

        # Current capital structure
        self.current_debt = 3825  # $M
        self.current_cash = 1215  # $M
        self.shares_outstanding = 117  # Million shares

    def calculate_wacc(self):
        """Calculate Weighted Average Cost of Capital"""
        cost_of_equity = self.risk_free_rate + self.beta * self.equity_risk_premium
        after_tax_cost_of_debt = self.cost_of_debt * (1 - self.tax_shield)

        wacc = (cost_of_equity * (1 - self.target_debt_ratio) +
                after_tax_cost_of_debt * self.target_debt_ratio)

        return wacc

    def build_revenue_forecast(self):
        """Build revenue forecast by segment"""
        lithium_revenue = {}
        prices = self.price_assumptions[self.scenario]

        for year in self.years:
            volume = self.production_volumes[year]
            price = prices[year]
            lithium_revenue[year] = (volume * price) / 1_000_000  # Convert to $M

        total_revenue = {
            year: lithium_revenue[year] + self.specialties_revenue
            for year in self.years
        }

        return lithium_revenue, total_revenue

    def build_ebitda_forecast(self, lithium_revenue, total_revenue):
        """Build EBITDA forecast"""
        ebitda = {}

        for year in self.years:
            # Lithium EBITDA
            volume = self.production_volumes[year]
            cash_cost = self.cash_costs[year]
            lithium_gross_profit = lithium_revenue[year] - (volume * cash_cost / 1_000_000)

            # Specialties EBITDA
            specialties_ebitda = self.specialties_revenue * self.specialties_ebitda_margin

            # Operating expenses
            rd_expense = total_revenue[year] * self.rd_pct_revenue
            total_opex = self.sga_fixed + rd_expense

            # Total EBITDA
            ebitda[year] = lithium_gross_profit + specialties_ebitda - total_opex

        return ebitda

    def build_fcf_forecast(self, ebitda, total_revenue):
        """Build Free Cash Flow forecast"""
        fcf = {}
        ppe = 12000  # Starting PP&E base
        working_capital = total_revenue[2025] * self.wc_pct_revenue

        for year in self.years:
            # EBIT (EBITDA - D&A)
            da = ppe * self.depreciation_rate
            ebit = ebitda[year] - da

            # NOPAT (Net Operating Profit After Tax)
            nopat = ebit * (1 - self.tax_rate)

            # Add back D&A
            cash_from_operations = nopat + da

            # Capex
            capex = self.capex_schedule[year]
            ppe += capex - da  # Update PP&E

            # Working capital change
            new_wc = total_revenue[year] * self.wc_pct_revenue
            wc_change = new_wc - working_capital
            working_capital = new_wc

            # Free Cash Flow
            fcf[year] = cash_from_operations - capex - wc_change

        return fcf

    def calculate_terminal_value(self, final_year_fcf):
        """Calculate terminal value using perpetuity growth model"""
        wacc = self.calculate_wacc()
        terminal_fcf = final_year_fcf * (1 + self.terminal_growth_rate)
        terminal_value = terminal_fcf / (wacc - self.terminal_growth_rate)
        return terminal_value

    def calculate_npv(self, fcf):
        """Calculate NPV of free cash flows"""
        wacc = self.calculate_wacc()
        npv = 0

        for i, year in enumerate(self.years):
            discount_factor = 1 / (1 + wacc) ** (i + 1)
            npv += fcf[year] * discount_factor

        # Add terminal value (discounted to present)
        final_year_fcf = fcf[self.years[-1]]
        terminal_value = self.calculate_terminal_value(final_year_fcf)
        terminal_pv = terminal_value / (1 + wacc) ** len(self.years)
        npv += terminal_pv

        return npv, terminal_pv

    def calculate_equity_value(self, enterprise_value):
        """Calculate equity value from enterprise value"""
        net_debt = self.current_debt - self.current_cash
        equity_value = enterprise_value - net_debt
        value_per_share = equity_value / self.shares_outstanding
        return equity_value, value_per_share

    def run_valuation(self):
        """Execute complete DCF valuation"""
        # Build forecasts
        lithium_rev, total_rev = self.build_revenue_forecast()
        ebitda = self.build_ebitda_forecast(lithium_rev, total_rev)
        fcf = self.build_fcf_forecast(ebitda, total_rev)

        # Calculate NPV
        enterprise_value, terminal_pv = self.calculate_npv(fcf)

        # Calculate equity value
        equity_value, price_per_share = self.calculate_equity_value(enterprise_value)

        # Create summary DataFrame
        summary = pd.DataFrame({
            'Year': self.years,
            'Lithium Revenue ($M)': [lithium_rev[y] for y in self.years],
            'Total Revenue ($M)': [total_rev[y] for y in self.years],
            'EBITDA ($M)': [ebitda[y] for y in self.years],
            'FCF ($M)': [fcf[y] for y in self.years],
            'Lithium Price ($/tonne)': [self.price_assumptions[self.scenario][y] for y in self.years],
            'Production (tonnes)': [self.production_volumes[y] for y in self.years]
        })

        results = {
            'scenario': self.scenario,
            'wacc': self.calculate_wacc(),
            'enterprise_value': enterprise_value,
            'terminal_value_pv': terminal_pv,
            'equity_value': equity_value,
            'price_per_share': price_per_share,
            'summary_table': summary
        }

        return results


# ============================================================================
# SCENARIO ANALYSIS
# ============================================================================

def run_scenario_analysis():
    """Run DCF across all three scenarios"""
    scenarios = ['bear', 'base', 'bull']
    results = {}

    for scenario in scenarios:
        model = AlbemarleDCF(scenario=scenario)
        results[scenario] = model.run_valuation()

    # Create comparison table
    comparison = pd.DataFrame({
        'Scenario': scenarios,
        'Enterprise Value ($M)': [results[s]['enterprise_value'] for s in scenarios],
        'Equity Value ($M)': [results[s]['equity_value'] for s in scenarios],
        'Price Per Share ($)': [results[s]['price_per_share'] for s in scenarios],
        'WACC': [results[s]['wacc'] for s in scenarios]
    })

    return results, comparison


# ============================================================================
# SENSITIVITY ANALYSIS
# ============================================================================

def sensitivity_analysis():
    """
    Perform sensitivity analysis on WACC and terminal growth rate
    """
    wacc_range = np.arange(0.06, 0.12, 0.01)
    terminal_growth_range = np.arange(0.00, 0.04, 0.005)

    sensitivity_matrix = np.zeros((len(wacc_range), len(terminal_growth_range)))

    base_model = AlbemarleDCF(scenario='base')
    lithium_rev, total_rev = base_model.build_revenue_forecast()
    ebitda = base_model.build_ebitda_forecast(lithium_rev, total_rev)
    fcf = base_model.build_fcf_forecast(ebitda, total_rev)

    for i, wacc in enumerate(wacc_range):
        for j, term_growth in enumerate(terminal_growth_range):
            # Modify model parameters
            base_model.terminal_growth_rate = term_growth

            # Calculate NPV with custom WACC
            npv = 0
            for idx, year in enumerate(base_model.years):
                discount_factor = 1 / (1 + wacc) ** (idx + 1)
                npv += fcf[year] * discount_factor

            # Terminal value
            final_fcf = fcf[base_model.years[-1]]
            terminal_fcf = final_fcf * (1 + term_growth)
            terminal_value = terminal_fcf / (wacc - term_growth)
            terminal_pv = terminal_value / (1 + wacc) ** len(base_model.years)
            npv += terminal_pv

            # Equity value per share
            equity_value = npv - (base_model.current_debt - base_model.current_cash)
            price_per_share = equity_value / base_model.shares_outstanding

            sensitivity_matrix[i, j] = price_per_share

    sensitivity_df = pd.DataFrame(
        sensitivity_matrix,
        index=[f'{w:.1%}' for w in wacc_range],
        columns=[f'{g:.1%}' for g in terminal_growth_range]
    )
    sensitivity_df.index.name = 'WACC'
    sensitivity_df.columns.name = 'Terminal Growth'

    return sensitivity_df


# ============================================================================
# MONTE CARLO SIMULATION
# ============================================================================

def monte_carlo_simulation(n_simulations=1000):
    """
    Perform Monte Carlo simulation on key valuation drivers
    """
    np.random.seed(42)

    results = []

    for _ in range(n_simulations):
        # Randomize key parameters
        lithium_price_multiplier = np.random.normal(1.0, 0.25)  # 25% std dev
        volume_multiplier = np.random.normal(1.0, 0.10)  # 10% std dev
        wacc_adjustment = np.random.normal(0, 0.015)  # +/- 150bps
        terminal_growth_adjustment = np.random.normal(0, 0.01)  # +/- 100bps

        # Create modified model
        model = AlbemarleDCF(scenario='base')

        # Adjust prices
        for year in model.years:
            model.price_assumptions['base'][year] *= lithium_price_multiplier
            model.production_volumes[year] *= volume_multiplier

        # Adjust WACC components
        model.beta += wacc_adjustment / model.equity_risk_premium  # Adjust beta to change WACC
        model.terminal_growth_rate += terminal_growth_adjustment

        # Run valuation
        result = model.run_valuation()
        results.append(result['price_per_share'])

    results_array = np.array(results)

    # Calculate statistics
    monte_carlo_stats = {
        'mean': np.mean(results_array),
        'median': np.median(results_array),
        'std_dev': np.std(results_array),
        'p10': np.percentile(results_array, 10),
        'p25': np.percentile(results_array, 25),
        'p75': np.percentile(results_array, 75),
        'p90': np.percentile(results_array, 90),
        'min': np.min(results_array),
        'max': np.max(results_array)
    }

    return monte_carlo_stats, results_array


# ============================================================================
# MAIN EXECUTION & OUTPUT
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("ALBEMARLE CORPORATION (ALB) - DCF VALUATION MODEL")
    print("=" * 80)
    print()

    # Run scenario analysis
    print("1. SCENARIO ANALYSIS")
    print("-" * 80)
    scenario_results, scenario_comparison = run_scenario_analysis()
    print(scenario_comparison.to_string(index=False))
    print()

    # Display base case details
    print("\n2. BASE CASE DETAILED PROJECTIONS")
    print("-" * 80)
    print(scenario_results['base']['summary_table'].to_string(index=False))
    print()

    print(f"\nBase Case WACC: {scenario_results['base']['wacc']:.2%}")
    print(f"Enterprise Value: ${scenario_results['base']['enterprise_value']:,.0f}M")
    print(f"Terminal Value (PV): ${scenario_results['base']['terminal_value_pv']:,.0f}M")
    print(f"Equity Value: ${scenario_results['base']['equity_value']:,.0f}M")
    print(f"Target Price: ${scenario_results['base']['price_per_share']:.2f}/share")
    print()

    # Sensitivity analysis
    print("\n3. SENSITIVITY ANALYSIS: Price Per Share ($)")
    print("-" * 80)
    sensitivity_table = sensitivity_analysis()
    print(sensitivity_table.round(2))
    print()

    # Monte Carlo simulation
    print("\n4. MONTE CARLO SIMULATION (1,000 iterations)")
    print("-" * 80)
    mc_stats, mc_results = monte_carlo_simulation(1000)

    print(f"Mean Price: ${mc_stats['mean']:.2f}")
    print(f"Median Price: ${mc_stats['median']:.2f}")
    print(f"Std Deviation: ${mc_stats['std_dev']:.2f}")
    print(f"\nPercentile Distribution:")
    print(f"  P10: ${mc_stats['p10']:.2f}")
    print(f"  P25: ${mc_stats['p25']:.2f}")
    print(f"  P75: ${mc_stats['p75']:.2f}")
    print(f"  P90: ${mc_stats['p90']:.2f}")
    print(f"\nRange: ${mc_stats['min']:.2f} - ${mc_stats['max']:.2f}")
    print()

    # Export to CSV
    print("\n5. EXPORTING RESULTS")
    print("-" * 80)

    scenario_comparison.to_csv('/home/user/TDITG/models/albemarle_scenario_analysis.csv', index=False)
    scenario_results['base']['summary_table'].to_csv('/home/user/TDITG/models/albemarle_base_projections.csv', index=False)
    sensitivity_table.to_csv('/home/user/TDITG/models/albemarle_sensitivity.csv')

    # Monte Carlo results
    mc_df = pd.DataFrame({
        'Simulation': range(1, len(mc_results) + 1),
        'Price_Per_Share': mc_results
    })
    mc_df.to_csv('/home/user/TDITG/models/albemarle_monte_carlo.csv', index=False)

    print("✓ albemarle_scenario_analysis.csv")
    print("✓ albemarle_base_projections.csv")
    print("✓ albemarle_sensitivity.csv")
    print("✓ albemarle_monte_carlo.csv")
    print()

    print("=" * 80)
    print("VALUATION COMPLETE")
    print("=" * 80)

    # Investment recommendation
    current_price = 85  # Assumed current market price
    base_target = scenario_results['base']['price_per_share']
    upside = (base_target - current_price) / current_price * 100

    print(f"\nCurrent Market Price: ${current_price:.2f}")
    print(f"Base Case Target: ${base_target:.2f}")
    print(f"Implied Upside/(Downside): {upside:+.1f}%")

    if upside > 20:
        print("\nRECOMMENDATION: BUY - Significant upside to fair value")
    elif upside > 0:
        print("\nRECOMMENDATION: HOLD - Modest upside, wait for better entry")
    else:
        print("\nRECOMMENDATION: SELL - Trading above fair value")
