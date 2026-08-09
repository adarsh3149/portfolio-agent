from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class MarketPriceResponse(BaseModel):
    id: int
    asset_id: int
    price: Decimal
    source: str
    price_time: datetime
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
