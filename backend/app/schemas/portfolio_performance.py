from decimal import Decimal

from pydantic import BaseModel


class PortfolioPerformance(BaseModel):
    total_invested: Decimal
    total_market_value: Decimal

    total_realized_profit_loss: Decimal
    total_unrealized_profit_loss: Decimal

    total_profit_loss: Decimal
