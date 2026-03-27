# import requests

# AMFI_URL = "https://www.amfiindia.com/spages/NAVAll.txt"


# def fetch_nav_data():
#     return requests.get(AMFI_URL).text


# def parse_nav_data(text):
#     nav_map = {}

#     for line in text.split("\n"):
#         parts = line.split(";")

#         if len(parts) > 4:
#             try:
#                 nav_map[parts[3].lower()] = float(parts[4])
#             except:
#                 continue

#     return nav_map

# import requests


# AMFI_URL = "https://www.amfiindia.com/spages/NAVAll.txt"


# def fetch_nav_data():
#     try:
#         response = requests.get(AMFI_URL)
#         return response.text
#     except Exception as e:
#         print("❌ Error fetching NAV:", e)
#         return None


# def parse_nav_data(raw_text):
#     nav_map = {}

#     lines = raw_text.split("\n")

#     for line in lines:
#         parts = line.split(";")

#         # Valid NAV line
#         if len(parts) > 4:
#             scheme_name = parts[3].strip().upper()
#             nav = parts[4]

#             try:
#                 nav = float(nav)
#             except:
#                 continue

#             nav_map[scheme_name] = nav

#     return nav_map


# def get_latest_nav():
#     raw = fetch_nav_data()

#     if not raw:
#         return {}

#     return parse_nav_data(raw)

import requests
import re
AMFI_URL = "https://www.amfiindia.com/spages/NAVAll.txt"


def fetch_nav_data():
    try:
        response = requests.get(AMFI_URL)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print("❌ Error fetching NAV:", e)
        return None




def normalize_name(name):
    name = name.upper()

    # Remove OPTION word
    name = name.replace("OPTION", "")

    # Remove extra spaces
    name = re.sub(r'\s+', ' ', name)

    # Extract core fund name
    fund_match = re.search(r'([A-Z\s]+FUND)', name)
    fund_name = fund_match.group(1).strip() if fund_match else name

    # Ensure DIRECT PLAN
    if "DIRECT PLAN" in name:
        plan = "DIRECT PLAN"
    else:
        plan = ""

    # Ensure GROWTH
    if "GROWTH" in name:
        growth = "GROWTH"
    else:
        growth = ""

    # Build canonical name
    final_name = f"{fund_name} {plan} {growth}".strip()

    return final_name


def parse_nav_data(text):
    nav_map = {}

    for line in text.split("\n"):
        parts = line.split(";")

        if len(parts) > 4:
            try:
                scheme_name = normalize_name(parts[3])
                nav = float(parts[4])

                nav_map[scheme_name] = nav
            except:
                continue

    return nav_map


def get_latest_nav():
    raw = fetch_nav_data()

    if not raw:
        return {}

    return parse_nav_data(raw)