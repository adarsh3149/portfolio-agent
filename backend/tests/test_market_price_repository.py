from datetime import UTC, datetime
from decimal import Decimal

from app.models.asset import Asset
from app.models.market_price import MarketPrice
from app.repositories.market_price_repository import MarketPriceRepository


def create_test_asset(db_session):

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

    return asset


def test_create_market_price(db_session):

    asset = create_test_asset(db_session)

    repository = MarketPriceRepository(db_session)

    market_price = MarketPrice(
        asset_id=asset.id,
        price=Decimal("1450.25"),
        source="test",
        price_time=datetime(
            2026,
            8,
            9,
            10,
            30,
            tzinfo=UTC,
        ),
    )

    result = repository.create(market_price)

    assert result.id is not None
    assert result.asset_id == asset.id
    assert result.price == Decimal("1450.25")
    assert result.source == "test"


def test_get_latest_market_price(db_session):

    asset = create_test_asset(db_session)

    repository = MarketPriceRepository(db_session)

    older_price = MarketPrice(
        asset_id=asset.id,
        price=Decimal("1440.00"),
        source="test",
        price_time=datetime(
            2026,
            8,
            9,
            10,
            0,
            tzinfo=UTC,
        ),
    )

    latest_price = MarketPrice(
        asset_id=asset.id,
        price=Decimal("1450.25"),
        source="test",
        price_time=datetime(
            2026,
            8,
            9,
            10,
            30,
            tzinfo=UTC,
        ),
    )

    repository.create(older_price)
    repository.create(latest_price)

    result = repository.get_latest_by_asset(
        asset.id
    )

    assert result is not None
    assert result.price == Decimal("1450.25")
    assert result.price_time == datetime(
        2026,
        8,
        9,
        10,
        30,
        tzinfo=UTC,
    )


def test_get_market_price_history(db_session):

    asset = create_test_asset(db_session)

    repository = MarketPriceRepository(db_session)

    first_price = MarketPrice(
        asset_id=asset.id,
        price=Decimal("1440.00"),
        source="test",
        price_time=datetime(
            2026,
            8,
            9,
            10,
            0,
            tzinfo=UTC,
        ),
    )

    second_price = MarketPrice(
        asset_id=asset.id,
        price=Decimal("1450.25"),
        source="test",
        price_time=datetime(
            2026,
            8,
            9,
            10,
            30,
            tzinfo=UTC,
        ),
    )

    third_price = MarketPrice(
        asset_id=asset.id,
        price=Decimal("1460.50"),
        source="test",
        price_time=datetime(
            2026,
            8,
            9,
            11,
            0,
            tzinfo=UTC,
        ),
    )

    repository.create(first_price)
    repository.create(second_price)
    repository.create(third_price)

    results = repository.get_history_by_asset(
        asset.id
    )

    assert len(results) == 3

    assert results[0].price == Decimal("1460.50")
    assert results[1].price == Decimal("1450.25")
    assert results[2].price == Decimal("1440.00")