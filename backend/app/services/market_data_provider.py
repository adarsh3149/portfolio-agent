from abc import ABC, abstractmethod
from decimal import Decimal


class MarketDataProvider(ABC):

    @abstractmethod
    def get_price(
        self,
        symbol: str,
    ) -> Decimal:
        raise NotImplementedError