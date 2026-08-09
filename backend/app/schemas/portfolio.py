from decimal import Decimal

from pydantic import BaseModel


class PortfolioSummary(BaseModel):
    total_holdings: int
    total_transactions: int
    total_invested: Decimal