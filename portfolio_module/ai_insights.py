# import ollama


# def generate_ai_insights(portfolio, nav_data, normalize_name):
#     summary = []

#     for fund, data in portfolio.items():
#         normalized = normalize_name(fund)
#         nav = nav_data.get(normalized)

#         if not nav:
#             continue

#         invested = data["total_invested"]
#         current = data["total_units"] * nav
#         profit = current - invested
#         percent = (profit / invested) * 100 if invested else 0

#         summary.append(
#             f"{fund}: Invested ₹{invested:.2f}, Current ₹{current:.2f}, P/L {percent:.2f}%"
#         )

#     summary_text = "\n".join(summary)

#     prompt = f"""
# You are a financial advisor.

# Analyze this portfolio:

# {summary_text}

# Give:
# 1. Risk analysis
# 2. Diversification suggestions
# 3. Overall portfolio health

# Keep it short and practical.
# """

#     response = ollama.chat(
#         model="llama3:8b",
#         messages=[{"role": "user", "content": prompt}]
#     )

#     return response["message"]["content"]

import os

USE_AI = os.getenv("USE_AI", "true")


def generate_ai_insights(portfolio, nav_data, normalize_name):
    # 🔥 Disable AI in cloud
    if USE_AI.lower() == "false":
        return "AI insights disabled in cloud mode."

    import ollama

    summary = []

    for fund, data in portfolio.items():
        normalized = normalize_name(fund)
        nav = nav_data.get(normalized)

        if not nav:
            continue

        invested = data["total_invested"]
        current = data["total_units"] * nav
        percent = ((current - invested) / invested) * 100 if invested else 0

        summary.append(
            f"{fund}: Invested ₹{invested:.2f}, Current ₹{current:.2f}, P/L {percent:.2f}%"
        )

    prompt = f"""
Analyze this portfolio and give short insights:

{chr(10).join(summary)}
"""

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]