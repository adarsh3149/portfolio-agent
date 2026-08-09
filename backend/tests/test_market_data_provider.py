from decimal import Decimal

import pytest

from app.services.fake_market_data_provider import (
    FakeMarketDataProvider,
)


def test_get_market_price():

    provider = FakeMarketDataProvider(
        {
            "INFY": Decimal("1450.25"),
        }
    )

    price = provider.get_price("INFY")

    assert price == Decimal("1450.25")


def test_get_market_price_for_unknown_symbol():

    provider = FakeMarketDataProvider(
        {
            "INFY": Decimal("1450.25"),
        }
    )

    with pytest.raises(ValueError):
        provider.get_price("UNKNOWN")
