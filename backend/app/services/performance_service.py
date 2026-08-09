from decimal import Decimal

from app.enums import TransactionType
from app.repositories.transaction_repository import (
    TransactionRepository,
)


class PerformanceService:

    def __init__(
        self,
        repository: TransactionRepository,
    ):
        self.repository = repository

    def get_realized_profit_loss(
        self,
        user_id: int,
    ) -> Decimal:

        transactions = self.repository.get_by_user(
            user_id
        )

        realized_profit_loss = Decimal("0")

        # Track cost basis independently for every asset.
        units_by_asset: dict[int, Decimal] = {}
        invested_by_asset: dict[int, Decimal] = {}

        for transaction in transactions:

            asset_id = transaction.asset_id

            units = units_by_asset.get(
                asset_id,
                Decimal("0"),
            )

            invested_amount = invested_by_asset.get(
                asset_id,
                Decimal("0"),
            )

            if transaction.transaction_type == TransactionType.BUY:

                units += transaction.quantity

                invested_amount += (
                    transaction.amount
                    + transaction.charges
                )

            elif transaction.transaction_type == TransactionType.SELL:

                if transaction.quantity > units:
                    raise ValueError(
                        "Cannot sell more units than owned."
                    )

                if units == Decimal("0"):
                    raise ValueError(
                        "Cannot sell when no units are owned."
                    )

                average_cost = (
                    invested_amount / units
                )

                cost_basis = (
                    average_cost
                    * transaction.quantity
                )

                realized_profit_loss += (
                    transaction.amount
                    - cost_basis
                    - transaction.charges
                )

                invested_amount -= cost_basis
                units -= transaction.quantity

            units_by_asset[asset_id] = units
            invested_by_asset[asset_id] = invested_amount

        return realized_profit_loss