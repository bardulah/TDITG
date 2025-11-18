#!/usr/bin/env python3
"""
Portfolio Scenario Models
Probability-weighted valuation scenarios for top holdings
"""

import json
from typing import Dict, List

def calculate_scenario_value(current_price: float, scenarios: Dict[str, Dict]) -> Dict:
    """Calculate expected value based on probability-weighted scenarios"""
    expected_value = 0
    results = {}

    for scenario_name, scenario_data in scenarios.items():
        target = scenario_data['target']
        prob = scenario_data['probability']
        upside = ((target - current_price) / current_price) * 100
        weighted_contribution = target * prob
        expected_value += weighted_contribution

        results[scenario_name] = {
            'target': target,
            'probability': prob,
            'upside_pct': round(upside, 1),
            'weighted_value': round(weighted_contribution, 2)
        }

    results['expected_value'] = round(expected_value, 2)
    results['expected_return'] = round(((expected_value - current_price) / current_price) * 100, 1)

    return results

# Top 10 Holdings by Current Value with Scenario Models

SCENARIO_MODELS = {
    'XPOA': {
        'current_price': 0.51,  # Actual price after bankruptcy
        'shares': 154.6137,
        'scenarios': {
            'bear': {'target': 0.00, 'probability': 0.95},  # Chapter 7 wipeout
            'base': {'target': 0.10, 'probability': 0.04},  # Minimal recovery
            'bull': {'target': 0.50, 'probability': 0.01},  # Unlikely restructure
        },
        'thesis': 'Chapter 7 bankruptcy filed Nov 14, 2025. Shareholders typically receive nothing.',
        'recommendation': 'SELL IMMEDIATELY'
    },

    'SNII': {
        'current_price': 24.40,  # Now Rigetti Computing
        'shares': 70.01928,
        'scenarios': {
            'bear': {'target': 6.00, 'probability': 0.25},   # Quantum winter
            'base': {'target': 15.00, 'probability': 0.45},  # Slow progress
            'bull': {'target': 30.00, 'probability': 0.25},  # Execution success
            'super_bull': {'target': 50.00, 'probability': 0.05},  # Breakthrough
        },
        'thesis': 'Rigetti Computing - quantum computing pure play. Behind IonQ but solid tech.',
        'recommendation': 'TRIM 50%'
    },

    'QUBT': {
        'current_price': 11.29,
        'shares': 27.1565,
        'scenarios': {
            'bear': {'target': 2.00, 'probability': 0.35},   # Fraud confirmed
            'base': {'target': 8.00, 'probability': 0.40},   # Legal overhang
            'bull': {'target': 20.00, 'probability': 0.20},  # Charges dismissed
            'super_bull': {'target': 35.00, 'probability': 0.05},  # Full vindication
        },
        'thesis': 'Securities fraud investigation ongoing. Multiple class actions filed.',
        'recommendation': 'SELL - Fraud risk too high'
    },

    'NVDA': {
        'current_price': 185.14,
        'shares': 1.3790163,
        'scenarios': {
            'bear': {'target': 120.00, 'probability': 0.15},  # AI spending slowdown
            'base': {'target': 200.00, 'probability': 0.45},  # Continued growth
            'bull': {'target': 280.00, 'probability': 0.35},  # Blackwell success
            'super_bull': {'target': 350.00, 'probability': 0.05},  # AI supercycle
        },
        'thesis': 'Dominant AI chip leader. $500B order backlog. Blackwell ramping.',
        'recommendation': 'HOLD through earnings'
    },

    'TSLA': {
        'current_price': 407.88,
        'shares': 0.7231181,
        'scenarios': {
            'bear': {'target': 200.00, 'probability': 0.20},  # EV competition
            'base': {'target': 350.00, 'probability': 0.40},  # Steady growth
            'bull': {'target': 500.00, 'probability': 0.30},  # FSD progress
            'super_bull': {'target': 700.00, 'probability': 0.10},  # Robotaxi launch
        },
        'thesis': 'EV leader with FSD optionality. Margins under pressure.',
        'recommendation': 'TRIM 25%'
    },

    'GOOGL': {
        'current_price': 284.54,
        'shares': 1.2895912,
        'scenarios': {
            'bear': {'target': 200.00, 'probability': 0.15},  # Antitrust breakup
            'base': {'target': 300.00, 'probability': 0.50},  # Steady execution
            'bull': {'target': 380.00, 'probability': 0.30},  # AI monetization
            'super_bull': {'target': 450.00, 'probability': 0.05},  # Gemini dominance
        },
        'thesis': 'AI leader with search moat. Antitrust ruling Nov 21.',
        'recommendation': 'HOLD'
    },

    'INTC': {
        'current_price': 34.44,
        'shares': 20.954951,
        'scenarios': {
            'bear': {'target': 18.00, 'probability': 0.25},   # Turnaround fails
            'base': {'target': 30.00, 'probability': 0.45},   # Slow progress
            'bull': {'target': 50.00, 'probability': 0.25},   # 18A success
            'super_bull': {'target': 70.00, 'probability': 0.05},  # Foundry wins
        },
        'thesis': 'Turnaround story. Stock up 90% YTD but foundry losing $2.3B/Q.',
        'recommendation': 'TAKE PARTIAL PROFITS'
    },

    'NET': {
        'current_price': 201.75,
        'shares': 2.246946,
        'scenarios': {
            'bear': {'target': 140.00, 'probability': 0.15},  # Growth decel
            'base': {'target': 220.00, 'probability': 0.45},  # Steady execution
            'bull': {'target': 300.00, 'probability': 0.35},  # Edge dominance
            'super_bull': {'target': 400.00, 'probability': 0.05},  # AI inference
        },
        'thesis': 'Edge computing leader. 28% growth, 15% margins. AWS competitor.',
        'recommendation': 'STRONG HOLD'
    },

    'AMD': {
        'current_price': 239.17,
        'shares': 1.0355337,
        'scenarios': {
            'bear': {'target': 150.00, 'probability': 0.15},  # AI share loss
            'base': {'target': 250.00, 'probability': 0.45},  # Steady growth
            'bull': {'target': 320.00, 'probability': 0.35},  # MI450 success
            'super_bull': {'target': 400.00, 'probability': 0.05},  # NVDA alternative
        },
        'thesis': 'AI datacenter growth. OpenAI partnership. 25% revenue growth.',
        'recommendation': 'HOLD/ACCUMULATE'
    },

    'MSFT': {
        'current_price': 503.00,
        'shares': 0.5122894,
        'scenarios': {
            'bear': {'target': 380.00, 'probability': 0.10},  # Cloud slowdown
            'base': {'target': 520.00, 'probability': 0.45},  # Steady growth
            'bull': {'target': 620.00, 'probability': 0.40},  # Copilot success
            'super_bull': {'target': 750.00, 'probability': 0.05},  # AI dominance
        },
        'thesis': 'Premier AI monetization play. Zero sell ratings. 16% growth.',
        'recommendation': 'STRONG BUY'
    }
}

def generate_scenario_report():
    """Generate comprehensive scenario analysis report"""

    print("=" * 80)
    print("PORTFOLIO SCENARIO MODELS - TOP 10 HOLDINGS")
    print("=" * 80)
    print()

    total_current_value = 0
    total_expected_value = 0

    for ticker, data in SCENARIO_MODELS.items():
        current = data['current_price']
        shares = data['shares']
        scenarios = data['scenarios']

        results = calculate_scenario_value(current, scenarios)

        current_value = current * shares
        expected_value = results['expected_value'] * shares

        total_current_value += current_value
        total_expected_value += expected_value

        print(f"\n{'='*60}")
        print(f"{ticker} - {data['recommendation']}")
        print(f"{'='*60}")
        print(f"Current Price: ${current:.2f} | Shares: {shares:.4f}")
        print(f"Current Value: ${current_value:.2f}")
        print(f"\nThesis: {data['thesis']}")
        print(f"\nScenarios:")

        for scenario_name, scenario_results in results.items():
            if scenario_name in ['expected_value', 'expected_return']:
                continue
            print(f"  {scenario_name.upper():12s}: ${scenario_results['target']:>7.2f} "
                  f"({scenario_results['upside_pct']:>+6.1f}%) "
                  f"@ {scenario_results['probability']*100:>4.0f}% prob")

        print(f"\n  EXPECTED VALUE: ${results['expected_value']:.2f}")
        print(f"  EXPECTED RETURN: {results['expected_return']:+.1f}%")
        print(f"  POSITION EV: ${expected_value:.2f}")

    print("\n" + "=" * 80)
    print("PORTFOLIO SUMMARY")
    print("=" * 80)
    print(f"\nTotal Current Value (Top 10): ${total_current_value:.2f}")
    print(f"Total Expected Value: ${total_expected_value:.2f}")
    print(f"Expected Portfolio Return: {((total_expected_value/total_current_value)-1)*100:+.1f}%")

    return {
        'total_current': total_current_value,
        'total_expected': total_expected_value,
        'models': SCENARIO_MODELS
    }

if __name__ == '__main__':
    generate_scenario_report()
