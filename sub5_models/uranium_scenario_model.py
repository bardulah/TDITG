"""
Uranium Mining Scenario Model for Denison Mines (DNN) and Ur-Energy (URG)
This model projects uranium prices and company valuations under multiple scenarios
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class UraniumPriceScenario:
    """Defines uranium price trajectory scenarios"""
    name: str
    prices: Dict[int, float]  # year -> $/lb U3O8
    probability: float

class UraniumMinerModel:
    """Models uranium mining company valuations"""

    def __init__(self):
        self.years = list(range(2025, 2036))
        self.risk_free_rate = 0.04

        # Uranium price scenarios
        self.scenarios = {
            'bear': UraniumPriceScenario(
                name='Bear Case',
                prices={
                    2025: 70, 2026: 65, 2027: 60, 2028: 65, 2029: 70,
                    2030: 75, 2031: 75, 2032: 75, 2033: 75, 2034: 75, 2035: 75
                },
                probability=0.20
            ),
            'base': UraniumPriceScenario(
                name='Base Case',
                prices={
                    2025: 85, 2026: 95, 2027: 100, 2028: 105, 2029: 100,
                    2030: 95, 2031: 95, 2032: 95, 2033: 95, 2034: 95, 2035: 95
                },
                probability=0.50
            ),
            'bull': UraniumPriceScenario(
                name='Bull Case',
                prices={
                    2025: 100, 2026: 120, 2027: 140, 2028: 150, 2029: 140,
                    2030: 130, 2031: 125, 2032: 120, 2033: 115, 2034: 115, 2035: 115
                },
                probability=0.25
            ),
            'super_bull': UraniumPriceScenario(
                name='Super Bull (SMR/AI Demand Spike)',
                prices={
                    2025: 110, 2026: 150, 2027: 180, 2028: 200, 2029: 180,
                    2030: 160, 2031: 150, 2032: 140, 2033: 135, 2034: 130, 2035: 125
                },
                probability=0.05
            )
        }

    def model_denison_mines(self) -> pd.DataFrame:
        """
        Model Denison Mines (DNN) valuation

        Key assumptions:
        - Wheeler River Phoenix production starts H1 2028
        - Gryphon development funded by Phoenix cash flows
        - Current share price: $2.39
        - Shares outstanding: ~900M
        """
        results = []

        for scenario_name, scenario in self.scenarios.items():
            # Production profile (M lbs U3O8)
            production = {
                2025: 0, 2026: 0, 2027: 0, 2028: 4.0, 2029: 8.0,
                2030: 8.0, 2031: 8.0, 2032: 8.0, 2033: 12.0, 2034: 15.0, 2035: 15.0
            }

            # Operating costs ($/lb)
            opex = {
                2025: 0, 2026: 0, 2027: 0, 2028: 35, 2029: 30,
                2030: 28, 2031: 26, 2032: 25, 2033: 28, 2034: 30, 2035: 30
            }

            # Capital expenditure (M$)
            capex = {
                2025: 50, 2026: 200, 2027: 150, 2028: 50, 2029: 20,
                2030: 150, 2031: 200, 2032: 100, 2033: 50, 2034: 30, 2035: 30
            }

            yearly_data = []
            for year in self.years:
                price = scenario.prices[year]
                prod = production[year]
                cost = opex[year]
                cap = capex[year]

                revenue = prod * price  # M$
                operating_cost = prod * cost  # M$
                gross_profit = revenue - operating_cost
                ebitda = gross_profit - 20  # G&A ~$20M/year

                # Tax at 25% when profitable
                tax = max(0, (ebitda - cap) * 0.25)
                fcf = ebitda - cap - tax

                yearly_data.append({
                    'Year': year,
                    'Scenario': scenario.name,
                    'U3O8_Price': price,
                    'Production_Mlbs': prod,
                    'Revenue_M': revenue,
                    'EBITDA_M': ebitda,
                    'CapEx_M': cap,
                    'FCF_M': fcf
                })

            # Calculate NPV
            discount_rate = 0.10  # 10% for uranium mining
            npv = 0
            for i, data in enumerate(yearly_data):
                npv += data['FCF_M'] / ((1 + discount_rate) ** (i + 1))

            # Terminal value (6x EBITDA multiple)
            terminal_ebitda = yearly_data[-1]['EBITDA_M']
            terminal_value = terminal_ebitda * 6 / ((1 + discount_rate) ** len(self.years))

            total_value = (npv + terminal_value) * 1_000_000  # Convert to $
            shares = 900_000_000
            price_target = total_value / shares

            results.append({
                'Scenario': scenario.name,
                'Probability': scenario.probability,
                'NPV_M': npv,
                'Terminal_Value_M': terminal_value * ((1 + discount_rate) ** len(self.years)),
                'Total_Value_M': (npv + terminal_value) * 1000 / 1000,
                'Price_Target': price_target,
                'Current_Price': 2.39,
                'Upside_Pct': (price_target / 2.39 - 1) * 100
            })

        return pd.DataFrame(results)

    def model_ur_energy(self) -> pd.DataFrame:
        """
        Model Ur-Energy (URG) valuation

        Key assumptions:
        - Lost Creek producing ~400k lbs/year currently
        - Shirley Basin online Q1 2026, ramps to 2.2M lbs combined
        - Current share price: $1.21
        - Shares outstanding: ~379M
        """
        results = []

        for scenario_name, scenario in self.scenarios.items():
            # Production profile (M lbs U3O8)
            production = {
                2025: 0.44, 2026: 1.0, 2027: 1.8, 2028: 2.2, 2029: 2.2,
                2030: 2.2, 2031: 2.2, 2032: 2.0, 2033: 1.8, 2034: 1.5, 2035: 1.2
            }

            # Contracted sales (at lower prices) vs spot
            contracted_pct = {
                2025: 1.0, 2026: 0.8, 2027: 0.6, 2028: 0.4, 2029: 0.3,
                2030: 0.3, 2031: 0.3, 2032: 0.3, 2033: 0.3, 2034: 0.2, 2035: 0.2
            }
            contracted_price = 60  # Average historical contract price

            # Operating costs ($/lb) - ISR is low cost
            opex = {
                2025: 51, 2026: 48, 2027: 45, 2028: 45, 2029: 45,
                2030: 45, 2031: 46, 2032: 48, 2033: 50, 2034: 52, 2035: 55
            }

            # Capital expenditure (M$)
            capex = {
                2025: 30, 2026: 25, 2027: 15, 2028: 10, 2029: 10,
                2030: 10, 2031: 10, 2032: 8, 2033: 8, 2034: 5, 2035: 5
            }

            yearly_data = []
            for year in self.years:
                spot_price = scenario.prices[year]
                prod = production[year]
                contracted = contracted_pct[year]

                # Blended realized price
                realized_price = contracted * contracted_price + (1 - contracted) * spot_price

                cost = opex[year]
                cap = capex[year]

                revenue = prod * realized_price  # M$
                operating_cost = prod * cost  # M$
                gross_profit = revenue - operating_cost
                ebitda = gross_profit - 8  # G&A ~$8M/year

                # Tax at 21% when profitable
                tax = max(0, (ebitda - cap) * 0.21)
                fcf = ebitda - cap - tax

                yearly_data.append({
                    'Year': year,
                    'Scenario': scenario.name,
                    'Spot_Price': spot_price,
                    'Realized_Price': realized_price,
                    'Production_Mlbs': prod,
                    'Revenue_M': revenue,
                    'EBITDA_M': ebitda,
                    'FCF_M': fcf
                })

            # Calculate NPV
            discount_rate = 0.12  # 12% for smaller producer
            npv = 0
            for i, data in enumerate(yearly_data):
                npv += data['FCF_M'] / ((1 + discount_rate) ** (i + 1))

            # Terminal value (5x EBITDA)
            terminal_ebitda = yearly_data[-1]['EBITDA_M']
            terminal_value = terminal_ebitda * 5 / ((1 + discount_rate) ** len(self.years))

            total_value = (npv + terminal_value) * 1_000_000
            shares = 379_000_000
            price_target = total_value / shares

            results.append({
                'Scenario': scenario.name,
                'Probability': scenario.probability,
                'NPV_M': npv,
                'Terminal_Value_M': terminal_value * ((1 + discount_rate) ** len(self.years)),
                'Price_Target': price_target,
                'Current_Price': 1.21,
                'Upside_Pct': (price_target / 1.21 - 1) * 100
            })

        return pd.DataFrame(results)

    def probability_weighted_targets(self) -> Dict:
        """Calculate probability-weighted price targets"""

        dnn_results = self.model_denison_mines()
        urg_results = self.model_ur_energy()

        dnn_weighted = sum(
            row['Price_Target'] * row['Probability']
            for _, row in dnn_results.iterrows()
        )

        urg_weighted = sum(
            row['Price_Target'] * row['Probability']
            for _, row in urg_results.iterrows()
        )

        return {
            'DNN': {
                'current_price': 2.39,
                'weighted_target': dnn_weighted,
                'upside_pct': (dnn_weighted / 2.39 - 1) * 100,
                'by_scenario': dnn_results.to_dict('records')
            },
            'URG': {
                'current_price': 1.21,
                'weighted_target': urg_weighted,
                'upside_pct': (urg_weighted / 1.21 - 1) * 100,
                'by_scenario': urg_results.to_dict('records')
            }
        }

def run_uranium_analysis():
    """Run complete uranium analysis and export results"""

    model = UraniumMinerModel()

    print("=" * 60)
    print("URANIUM MINING SCENARIO ANALYSIS")
    print("=" * 60)

    # Denison Mines
    print("\n--- DENISON MINES (DNN) ---")
    dnn_results = model.model_denison_mines()
    print(dnn_results.to_string(index=False))

    # Ur-Energy
    print("\n--- UR-ENERGY (URG) ---")
    urg_results = model.model_ur_energy()
    print(urg_results.to_string(index=False))

    # Probability-weighted targets
    print("\n--- PROBABILITY-WEIGHTED PRICE TARGETS ---")
    weighted = model.probability_weighted_targets()

    print(f"\nDenison Mines (DNN):")
    print(f"  Current Price: ${weighted['DNN']['current_price']:.2f}")
    print(f"  Weighted Target: ${weighted['DNN']['weighted_target']:.2f}")
    print(f"  Expected Upside: {weighted['DNN']['upside_pct']:.1f}%")

    print(f"\nUr-Energy (URG):")
    print(f"  Current Price: ${weighted['URG']['current_price']:.2f}")
    print(f"  Weighted Target: ${weighted['URG']['weighted_target']:.2f}")
    print(f"  Expected Upside: {weighted['URG']['upside_pct']:.1f}%")

    # Export to CSV
    dnn_results.to_csv('/home/user/TDITG/sub5_models/dnn_scenario_results.csv', index=False)
    urg_results.to_csv('/home/user/TDITG/sub5_models/urg_scenario_results.csv', index=False)

    print("\n[Results exported to CSV files]")

    return weighted

if __name__ == "__main__":
    results = run_uranium_analysis()
