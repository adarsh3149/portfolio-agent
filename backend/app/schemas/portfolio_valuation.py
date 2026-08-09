from decimal import Decimal

from pydantic import BaseModel


class PortfolioValuation(BaseModel):
    asset_id: int
    symbol: str

    units: Decimal
    invested_amount: Decimal

    current_price: Decimal
    market_value: Decimal

    unrealized_profit_loss: Decimal
    unrealized_profit_loss_percentage: Decimal
