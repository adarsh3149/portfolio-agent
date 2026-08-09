from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.market_price import MarketPrice


class MarketPriceRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        market_price: MarketPrice,
    ) -> MarketPrice:

        self.db.add(market_price)
        self.db.commit()
        self.db.refresh(market_price)

        return market_price

    def get_latest_by_asset(
        self,
        asset_id: int,
    ) -> MarketPrice | None:

        statement = (
            select(MarketPrice)
            .where(
                MarketPrice.asset_id == asset_id
            )
            .order_by(
                MarketPrice.price_time.desc()
            )
            .limit(1)
        )

        return self.db.scalar(statement)

    def get_history_by_asset(
        self,
        asset_id: int,
    ) -> list[MarketPrice]:

        statement = (
            select(MarketPrice)
            .where(
                MarketPrice.asset_id == asset_id
            )
            .order_by(
                MarketPrice.price_time.desc()
            )
        )

        return list(
            self.db.scalars(statement)
        )