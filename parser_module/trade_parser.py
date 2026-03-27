import re


def clean_text(text):
    """Normalize whitespace"""
    return re.sub(r'\s+', ' ', text)


def parse_coin_email(body):
    text = clean_text(body)

    # 🔥 Precise regex to capture ONLY valid fund names
    pattern = re.findall(
        r'([A-Z][A-Z\s]+FUND\s*\-\s*DIRECT PLAN.*?OPTION)\s+Folio.*?NAV:\s*₹([\d\.]+).*?₹(\d+)\s+([\d\.]+)\s+units',
        text
    )

    results = []

    for match in pattern:
        fund_name = match[0].strip().upper()  # normalize

        nav = float(match[1])
        amount = float(match[2])
        units = float(match[3])

        results.append({
            "type": "MF",
            "fund": fund_name.upper(),
            "nav": nav,
            "amount": amount,
            "units": units
        })

    return results if results else None