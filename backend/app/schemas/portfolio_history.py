from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class PortfolioHistory(BaseModel):
    snapshot_date: date

    total_invested: Decimal
    total_market_value: Decimal

    total_realized_profit_loss: Decimal
    total_unrealized_profit_loss: Decimal

    total_profit_loss: Decimal
