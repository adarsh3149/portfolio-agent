from decimal import Decimal

from app.models.cdsl_transaction_event import CDSLTransactionEvent
from app.models.transaction import Transaction
from app.repositories.asset_repository import AssetRepository
from app.repositories.cdsl_transaction_event_repository import (
    CDSLTransactionEventRepository,
)
from app.repositories.market_price_repository import MarketPriceRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.cdsl import CDSLTransactionDirection
from app.enums import TransactionType


class CDSLTransactionProcessor:

    def __init__(
        self,
        event_repository: CDSLTransactionEventRepository,
        asset_repository: AssetRepository,
        market_price_repository: MarketPriceRepository,
        transaction_repository: TransactionRepository,
    ):
        self.event_repository = event_repository
        self.asset_repository = asset_repository
        self.market_price_repository = market_price_repository
        self.transaction_repository = transaction_repository

    def process_event(
        self,
        event: CDSLTransactionEvent,
    ) -> Transaction | None:

        if event.processed:
            return None

        asset = self.asset_repository.get_by_isin(
            event.isin,
        )

        if asset is None:
            return None

        market_price = (
            self.market_price_repository.get_latest_by_asset(
                asset.id,
            )
        )

        if market_price is None:
            return None

        price = Decimal(str(market_price.price))

        if price <= Decimal("0"):
            return None

        if event.direction == CDSLTransactionDirection.CREDIT:
            transaction_type = TransactionType.BUY
        else:
            transaction_type = TransactionType.SELL

        amount = event.quantity * price

        transaction = Transaction(
            user_id=event.user_id,
            asset_id=asset.id,
            transaction_type=transaction_type,
            quantity=event.quantity,
            price=price,
            amount=amount,
            charges=Decimal("0.00"),
            transaction_date=event.transaction_datetime.date(),
            notes=(
                f"Imported from CDSL event "
                f"{event.id} ({event.source_reference})"
            ),
        )

        transaction = self.transaction_repository.create(
            transaction,
        )

        self.event_repository.mark_processed(
            event,
        )

        return transaction

    def process_unprocessed_events(
        self,
        user_id: int,
    ) -> list[Transaction]:
        transactions: list[Transaction] = []

        for event in self.event_repository.get_unprocessed_by_user(
            user_id,
        ):
            transaction = self.process_event(event)

            if transaction is not None:
                transactions.append(transaction)

        return transactions
