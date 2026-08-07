from enum import Enum


class AssetType(str, Enum):
    STOCK = "STOCK"
    MUTUAL_FUND = "MUTUAL_FUND"
    ETF = "ETF"
    GOLD = "GOLD"
    FIXED_DEPOSIT = "FIXED_DEPOSIT"