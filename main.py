# from email_module.email_reader import fetch_emails
# from parser_module.trade_parser import parse_coin_email
# from portfolio_module.portfolio_manager import build_portfolio
# from portfolio_module.nav_fetcher import get_latest_nav, normalize_name
# from portfolio_module.report_generator import generate_report
# from utils.email_sender import send_email
# from portfolio_module.ai_insights import generate_ai_insights


# emails = fetch_emails("Zerodha/Allotment")

# all_trades = []

# for e in emails:
#     parsed = parse_coin_email(e["body"])
    
#     if parsed:
#         all_trades.extend(parsed)


# portfolio = build_portfolio(all_trades)

# nav_data = get_latest_nav()

# report = generate_report(portfolio, nav_data, normalize_name)

# print(report)

# ai_text = generate_ai_insights(portfolio, nav_data, normalize_name)

# print("\n🤖 AI Insights:\n")
# print(ai_text)

# # 🔥 Send email
# send_email("Daily Portfolio Report 📊", report)
# # normalized_fund = normalize_name(fund)
# # nav = nav_data.get(normalized_fund)

# print("\n📊 Portfolio Summary:\n")

# for fund, data in portfolio.items():
#     normalized_fund = normalize_name(fund)

#     latest_nav = nav_data.get(normalized_fund)

#     if latest_nav:
#         current_value = data["total_units"] * latest_nav
#         profit = current_value - data["total_invested"]
#         profit_percent = (profit / data["total_invested"]) * 100
#     else:
#         current_value = 0
#         profit = 0
#         profit_percent = 0

#     print(f"\n{fund}")
#     print(f"Units: {data['total_units']:.3f}")
#     print(f"Invested: ₹{data['total_invested']:.2f}")
#     print(f"Avg NAV: ₹{data['avg_nav']:.2f}")

#     if latest_nav:
#         print(f"Current NAV: ₹{latest_nav:.2f}")
#         print(f"Current Value: ₹{current_value:.2f}")
#         print(f"Profit/Loss: ₹{profit:.2f} ({profit_percent:.2f}%)")
#     else:
#         print("⚠️ NAV not found")

from email_module.email_reader import fetch_emails
from parser_module.trade_parser import parse_coin_email
from portfolio_module.portfolio_manager import build_portfolio
from portfolio_module.nav_fetcher import get_latest_nav, normalize_name
from portfolio_module.report_generator import generate_report
from portfolio_module.ai_insights import generate_ai_insights
from utils.email_sender import send_email

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)


def main():
    # raise Exception("Test failure")

    logging.info("📥 Fetching emails...")
    emails = fetch_emails("Zerodha/Allotment")

    # 🔥 Step 1: Parse trades
    all_trades = []

    for e in emails:
        parsed = parse_coin_email(e["body"])
        if parsed:
            all_trades.extend(parsed)

    if not all_trades:
        print("⚠️ No trades found.")
        return

    # 🔥 Step 2: Build portfolio
    print("📊 Building portfolio...")
    portfolio = build_portfolio(all_trades)

    # 🔥 Step 3: Fetch NAV
    print("🌐 Fetching latest NAV...")
    nav_data = get_latest_nav()

    # 🔥 Step 4: Generate report
    print("📝 Generating report...")
    report = generate_report(portfolio, nav_data, normalize_name)

    # 🔥 Step 5: Generate AI insights
    print("🤖 Generating AI insights...")
    ai_text = generate_ai_insights(portfolio, nav_data, normalize_name)

    # 🔥 Combine report
    final_report = report + "\n\n🤖 AI Insights:\n" + ai_text

    print("\n" + "="*50)
    print(final_report)
    print("="*50)

    # 🔥 Step 6: Send email
    print("📧 Sending email...")
    send_email(
    "Daily Portfolio Report 📊",
    {
        "report": report,
        "ai": ai_text
    }
)


if __name__ == "__main__":
    main()