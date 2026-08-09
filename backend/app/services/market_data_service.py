from datetime import UTC, datetime

from fastapi import HTTPException, status

from app.models.market_price import MarketPrice
from app.repositories.asset_repository import AssetRepository
from app.repositories.market_price_repository import MarketPriceRepository
from app.services.market_data_provider import MarketDataProvider


class MarketDataService:

    def __init__(
        self,
        asset_repository: AssetRepository,
        market_price_repository: MarketPriceRepository,
        provider: MarketDataProvider,
    ):
        self.asset_repository = asset_repository
        self.market_price_repository = market_price_repository
        self.provider = provider

    def fetch_and_store_price(
        self,
        asset_id: int,
    ) -> MarketPrice:

        asset = self.asset_repository.get_by_id(
            asset_id
        )

        if asset is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset with ID '{asset_id}' not found.",
            )

        price = self.provider.get_price(
            asset.symbol
        )

        market_price = MarketPrice(
            asset_id=asset.id,
            price=price,
            source="provider",
            price_time=datetime.now(UTC),
        )

        return self.market_price_repository.create(
            market_price
        )
