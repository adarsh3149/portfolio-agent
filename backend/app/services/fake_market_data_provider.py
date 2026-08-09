from decimal import Decimal

from app.services.market_data_provider import MarketDataProvider


class FakeMarketDataProvider(MarketDataProvider):

    def __init__(
        self,
        prices: dict[str, Decimal],
    ):
        self.prices = prices

    def get_price(
        self,
        symbol: str,
    ) -> Decimal:

        price = self.prices.get(symbol)

        if price is None:
            raise ValueError(
                f"No market price available for '{symbol}'."
            )

        return price