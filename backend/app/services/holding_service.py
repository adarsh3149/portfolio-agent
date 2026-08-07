from decimal import Decimal

from app.models.transaction import Transaction
from app.repositories.transaction_repository import TransactionRepository
from app.services.holding_accumulator import HoldingAccumulator
from app.schemas.holding import Holding
from app.enums import TransactionType


class HoldingService:

    def __init__(
        self,
        repository: TransactionRepository,
    ):
        self.repository = repository

    def _process_buy(
        self,
        state: HoldingAccumulator,
        transaction: Transaction,
    ):
        state.units += transaction.quantity

        state.invested_amount += (
            transaction.amount +
            transaction.charges
        )

    def _process_sell(
        self,
        state: HoldingAccumulator,
        transaction: Transaction,
    ):
        if transaction.quantity > state.units:
            raise ValueError(
            "Cannot sell more units than owned."
        )

        average_cost = (
            state.invested_amount /
            state.units
        )

        state.invested_amount -= (
            average_cost *
            transaction.quantity
       )

        state.units -= transaction.quantity

    def _build_holding(
            self,
            accumulator: HoldingAccumulator,
    ) -> Holding:
        if accumulator.units == Decimal("0"):
            average_cost = Decimal("0")
        else:
            average_cost = (
            accumulator.invested_amount /
            accumulator.units
        )

        return Holding(
            asset_id=accumulator.asset_id,
            symbol=accumulator.symbol,
            asset_name=accumulator.asset_name,
            units=accumulator.units,
            average_cost=average_cost,
            invested_amount=accumulator.invested_amount,
        )

    def get_holdings(
        self,
        user_id: int,
    ) -> list[Holding]:

        transactions = self.repository.get_by_user(user_id)

        accumulators: dict[int, HoldingAccumulator] = {}

        for transaction in transactions:
            accumulator = accumulators.get(
                transaction.asset_id
            )

            if accumulator is None:

                accumulator = HoldingAccumulator(
                    asset_id=transaction.asset.id,
                    symbol=transaction.asset.symbol,
                    asset_name=transaction.asset.name,
                )

                accumulators[
                    transaction.asset_id
                ] = accumulator

            if transaction.transaction_type == TransactionType.BUY:

                self._process_buy(
                    accumulator,
                    transaction,
                )

            elif transaction.transaction_type == TransactionType.SELL:

                self._process_sell(
                    accumulator,
                    transaction,
                )

        

        return [
            self._build_holding(accumulator)
            for accumulator in accumulators.values()
        ]