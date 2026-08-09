from decimal import Decimal

from app.models.asset import Asset
from app.repositories.asset_repository import AssetRepository
from app.repositories.market_price_repository import MarketPriceRepository
from app.services.fake_market_data_provider import (
    FakeMarketDataProvider,
)
from app.services.market_data_service import MarketDataService


def test_fetch_and_store_price(db_session):

    asset = Asset(
        symbol="INFY",
        name="Infosys",
        asset_type="STOCK",
        exchange="NSE",
        currency="INR",
    )

    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)

    provider = FakeMarketDataProvider(
        {
            "INFY": Decimal("1450.25"),
        }
    )

    service = MarketDataService(
        asset_repository=AssetRepository(db_session),
        market_price_repository=MarketPriceRepository(
            db_session
        ),
        provider=provider,
    )

    result = service.fetch_and_store_price(
        asset.id
    )

    assert result.id is not None
    assert result.asset_id == asset.id
    assert result.price == Decimal("1450.25")
    assert result.source == "provider"


def test_fetch_price_for_unknown_asset(db_session):

    provider = FakeMarketDataProvider(
        {
            "INFY": Decimal("1450.25"),
        }
    )

    service = MarketDataService(
        asset_repository=AssetRepository(db_session),
        market_price_repository=MarketPriceRepository(
            db_session
        ),
        provider=provider,
    )

    from fastapi import HTTPException

    try:
        service.fetch_and_store_price(999999)
        assert False
    except HTTPException as exc:
        assert exc.status_code == 404
