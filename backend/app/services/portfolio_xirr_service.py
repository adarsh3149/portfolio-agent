from datetime import date
from decimal import Decimal

from app.enums import TransactionType
from app.repositories.portfolio_snapshot_repository import (
    PortfolioSnapshotRepository,
)
from app.repositories.transaction_repository import (
    TransactionRepository,
)
from app.services.xirr_service import XIRRService


class PortfolioXIRRService:

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        snapshot_repository: PortfolioSnapshotRepository,
    ):
        self.transaction_repository = transaction_repository
        self.snapshot_repository = snapshot_repository
        self.xirr_service = XIRRService()

    def calculate(
        self,
        user_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> Decimal:

        transactions = (
            self.transaction_repository.get_by_user(
                user_id=user_id,
            )
        )

        if not transactions:
            raise ValueError(
                "At least one transaction is required."
            )

        snapshots = (
            self.snapshot_repository.get_by_user(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
            )
        )

        if not snapshots:
            raise ValueError(
                "A portfolio snapshot is required."
            )

        latest_snapshot = snapshots[-1]

        cash_flows: list[
            tuple[date, Decimal]
        ] = []

        for transaction in transactions:

            if (
                start_date is not None
                and transaction.transaction_date
                < start_date
            ):
                continue

            if (
                end_date is not None
                and transaction.transaction_date
                > end_date
            ):
                continue

            if transaction.transaction_type == (
                TransactionType.BUY
            ):
                cash_flow = -(
                    transaction.amount
                    + transaction.charges
                )

            elif transaction.transaction_type == (
                TransactionType.SELL
            ):
                cash_flow = (
                    transaction.amount
                    - transaction.charges
                )

            else:
                continue

            cash_flows.append(
                (
                    transaction.transaction_date,
                    cash_flow,
                )
            )

        if not cash_flows:
            raise ValueError(
                "At least one transaction is required."
            )

        cash_flows.append(
            (
                latest_snapshot.snapshot_date,
                latest_snapshot.total_market_value,
            )
        )

        return self.xirr_service.calculate(
            cash_flows=cash_flows,
        )
