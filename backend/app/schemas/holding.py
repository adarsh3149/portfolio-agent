from decimal import Decimal

from pydantic import BaseModel


class Holding(BaseModel):
    asset_id: int
    symbol: str
    asset_name: str

    units: Decimal
    average_cost: Decimal
    invested_amount: Decimal