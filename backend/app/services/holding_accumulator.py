from dataclasses import dataclass
from decimal import Decimal


@dataclass
class HoldingAccumulator:
    asset_id: int
    symbol: str
    asset_name: str

    units: Decimal = Decimal("0")
    invested_amount: Decimal = Decimal("0")