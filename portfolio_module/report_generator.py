# def generate_report(portfolio, nav_data, normalize_name):
#     total_invested = 0
#     total_current = 0

#     fund_performance = []

#     for fund, data in portfolio.items():
#         normalized = normalize_name(fund)
#         nav = nav_data.get(normalized)

#         if not nav:
#             continue

#         invested = data["total_invested"]
#         current = data["total_units"] * nav
#         profit = current - invested

#         total_invested += invested
#         total_current += current

#         fund_performance.append((fund, profit))

#     total_profit = total_current - total_invested
#     profit_percent = (total_profit / total_invested) * 100 if total_invested else 0

#     # 🔥 Find best & worst
#     best = max(fund_performance, key=lambda x: x[1])[0]
#     worst = min(fund_performance, key=lambda x: x[1])[0]

#     report = f"""
# 📊 Portfolio Report

# Total Invested: ₹{total_invested:.2f}
# Current Value: ₹{total_current:.2f}
# Profit/Loss: ₹{total_profit:.2f} ({profit_percent:.2f}%)

# 🏆 Best Performer: {best}
# 📉 Worst Performer: {worst}
# """

#     return report

def generate_report(portfolio, nav_data, normalize_name):
    total_invested = 0
    total_current = 0

    fund_details = []

    for fund, data in portfolio.items():
        normalized = normalize_name(fund)
        nav = nav_data.get(normalized)

        if not nav:
            continue

        invested = data["total_invested"]
        units = data["total_units"]
        current = units * nav
        profit = current - invested
        percent = (profit / invested) * 100 if invested else 0

        total_invested += invested
        total_current += current

        fund_details.append({
            "fund": fund,
            "invested": invested,
            "current": current,
            "profit": profit,
            "percent": percent
        })

    total_profit = total_current - total_invested
    total_percent = (total_profit / total_invested) * 100 if total_invested else 0

    # 🔥 Sort funds by performance
    fund_details.sort(key=lambda x: x["percent"], reverse=True)

    # 🔥 Build fund breakdown text
    fund_text = ""
    for f in fund_details:
        emoji = "🟢" if f["profit"] >= 0 else "🔴"

        fund_text += f"""
{emoji} {f['fund']}
Invested: ₹{f['invested']:.2f}
Current: ₹{f['current']:.2f}
P/L: ₹{f['profit']:.2f} ({f['percent']:.2f}%)
"""

    report = f"""
📊 DAILY PORTFOLIO REPORT

━━━━━━━━━━━━━━━━━━━━━━━
💰 Total Invested: ₹{total_invested:.2f}
📈 Current Value: ₹{total_current:.2f}
📊 Total P/L: ₹{total_profit:.2f} ({total_percent:.2f}%)
━━━━━━━━━━━━━━━━━━━━━━━

📌 FUND BREAKDOWN:
{fund_text}

━━━━━━━━━━━━━━━━━━━━━━━
"""

    return report