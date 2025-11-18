"""
Portfolio Analysis Tool for User Portfolio
Calculates key metrics, identifies risks, and generates recommendations
"""

import json
from collections import defaultdict
from typing import Dict, List, Tuple

def analyze_portfolio(portfolio_data: List[Dict]) -> Dict:
    """Analyze portfolio and generate metrics"""

    # Calculate key metrics
    total_invested = 0
    total_current_value = 0
    total_ppl = 0

    winners = []
    losers = []
    high_risk = []

    # Sector classification (simplified)
    sectors = defaultdict(list)

    for holding in portfolio_data:
        ticker = holding['ticker'].replace('_US_EQ', '').replace('_EQ', '')
        qty = holding['quantity']
        avg_price = holding['averagePrice']
        current_price = holding['currentPrice']
        ppl = holding.get('ppl', 0) or 0

        invested = qty * avg_price
        current_value = qty * current_price

        total_invested += invested
        total_current_value += current_value
        total_ppl += ppl

        # Calculate return percentage
        if invested > 0:
            return_pct = ((current_value - invested) / invested) * 100
        else:
            return_pct = 0

        position_data = {
            'ticker': ticker,
            'quantity': qty,
            'avg_price': avg_price,
            'current_price': current_price,
            'invested': invested,
            'current_value': current_value,
            'ppl': ppl,
            'return_pct': return_pct
        }

        # Categorize winners/losers
        if ppl > 50:
            winners.append(position_data)
        elif ppl < -20:
            losers.append(position_data)

        # Identify high-risk (near-zero stocks)
        if current_price < 0.10 or return_pct < -90:
            high_risk.append(position_data)

    # Sort by P/L
    winners.sort(key=lambda x: x['ppl'], reverse=True)
    losers.sort(key=lambda x: x['ppl'])

    return {
        'total_invested': total_invested,
        'total_current_value': total_current_value,
        'total_ppl': total_ppl,
        'overall_return_pct': ((total_current_value - total_invested) / total_invested * 100) if total_invested > 0 else 0,
        'num_positions': len(portfolio_data),
        'top_winners': winners[:15],
        'top_losers': losers[:15],
        'high_risk': high_risk
    }

def generate_report(analysis: Dict) -> str:
    """Generate detailed portfolio report"""

    report = []
    report.append("=" * 70)
    report.append("PORTFOLIO ANALYSIS REPORT")
    report.append("=" * 70)

    # Summary metrics
    report.append("\n## PORTFOLIO SUMMARY")
    report.append(f"Total Positions: {analysis['num_positions']}")
    report.append(f"Total Invested: ${analysis['total_invested']:,.2f}")
    report.append(f"Current Value: ${analysis['total_current_value']:,.2f}")
    report.append(f"Total P/L: ${analysis['total_ppl']:,.2f}")
    report.append(f"Overall Return: {analysis['overall_return_pct']:.1f}%")

    # Top Winners
    report.append("\n## TOP WINNERS (P/L > $50)")
    report.append("-" * 70)
    for pos in analysis['top_winners']:
        report.append(f"{pos['ticker']:12} | P/L: ${pos['ppl']:>10,.2f} | Return: {pos['return_pct']:>7.1f}% | Current: ${pos['current_price']:.2f}")

    # Top Losers
    report.append("\n## TOP LOSERS (P/L < -$20)")
    report.append("-" * 70)
    for pos in analysis['top_losers']:
        report.append(f"{pos['ticker']:12} | P/L: ${pos['ppl']:>10,.2f} | Return: {pos['return_pct']:>7.1f}% | Current: ${pos['current_price']:.2f}")

    # High Risk Positions
    report.append("\n## HIGH RISK POSITIONS (Near-Zero or >90% Loss)")
    report.append("-" * 70)
    for pos in analysis['high_risk']:
        report.append(f"{pos['ticker']:12} | Current: ${pos['current_price']:.4f} | Return: {pos['return_pct']:.1f}%")

    return "\n".join(report)

# Run analysis
if __name__ == "__main__":
    with open('/home/user/TDITG/portfolio.json', 'r') as f:
        portfolio = json.load(f)

    analysis = analyze_portfolio(portfolio)
    report = generate_report(analysis)
    print(report)
