# def normalize(text):
#     text = text.lower()

#     remove_words = ["direct", "plan", "growth", "option"]

#     for word in remove_words:
#         text = text.replace(word, "")

#     text = text.replace("-", " ")
#     text = " ".join(text.split())

#     return text.strip()


# def build_portfolio(merged_trades):
#     portfolio = {}

#     for trade in merged_trades:
#         key = normalize(trade["fund"])

#         if key not in portfolio:
#             portfolio[key] = {
#                 "fund": trade["fund"],
#                 "total_units": 0,
#                 "total_invested": 0
#             }

#         portfolio[key]["total_units"] += trade["units"]
#         portfolio[key]["total_invested"] += trade["amount"]

#     return list(portfolio.values())


# def calculate_portfolio_value(portfolio, nav_map):
#     results = []

#     for fund in portfolio:
#         fund_key = normalize(fund["fund"])

#         print("\n🔍 Checking fund:", fund_key)

#         nav = None

#         for scheme, value in nav_map.items():
#             scheme_key = normalize(scheme)

#             if fund_key in scheme_key or scheme_key in fund_key:
#                 nav = value
#                 print("✅ MATCH FOUND:", scheme)
#                 break

#         if nav:
#             current_value = fund["total_units"] * nav
#             profit = current_value - fund["total_invested"]

#             results.append({
#                 "fund": fund["fund"],
#                 "invested": round(fund["total_invested"], 2),
#                 "units": round(fund["total_units"], 3),
#                 "nav": nav,
#                 "current_value": round(current_value, 2),
#                 "profit": round(profit, 2)
#             })
#         else:
#             print("❌ NO NAV MATCH for:", fund["fund"])

#     return results

def build_portfolio(trades):
    portfolio = {}

    for trade in trades:
        fund = trade["fund"]

        if fund not in portfolio:
            portfolio[fund] = {
                "total_units": 0,
                "total_invested": 0
            }

        portfolio[fund]["total_units"] += trade["units"]
        portfolio[fund]["total_invested"] += trade["amount"]

    # 🔥 Calculate average NAV (cost price)
    for fund in portfolio:
        units = portfolio[fund]["total_units"]
        invested = portfolio[fund]["total_invested"]

        portfolio[fund]["avg_nav"] = invested / units if units else 0

    return portfolio