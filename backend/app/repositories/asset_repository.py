from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset


class AssetRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
            self,
            asset:Asset,
    ) -> Asset:
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def get_by_id(
        self,
        asset_id: int,
    ) -> Asset | None:

        statement = (
            select(Asset)
            .where(
                Asset.id == asset_id
            )
        )

        return self.db.scalar(statement)

    def get_by_symbol(
            self,
            symbol: str,
    ) -> Asset | None:

        statement = (
            select(Asset)
            .where(
                Asset.symbol == symbol
            )
        )
        return self.db.scalar(statement)

    def get_all(
            self,
    ) -> list[Asset]:

        statement = (
            select(Asset)
            .order_by(
                Asset.symbol,
            )
        )

        return list(
            self.db.scalars(statement)
        )