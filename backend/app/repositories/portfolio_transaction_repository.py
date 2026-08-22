from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.portfolio_transaction import (
    PortfolioTransaction,
)


class PortfolioTransactionRepository:

    def __init__(
        self,
        db_session: Session,
    ):
        self.db_session = db_session

    def create(
        self,
        user_id: int,
        isin: str,
        security_name: str,
        transaction_date: date,
        transaction_type: str,
        quantity: Decimal,
        source: str,
        source_reference: str,
    ) -> PortfolioTransaction:

        transaction = PortfolioTransaction(
            user_id=user_id,
            isin=isin,
            security_name=security_name,
            transaction_date=transaction_date,
            transaction_type=transaction_type,
            quantity=quantity,
            source=source,
            source_reference=source_reference,
        )

        self.db_session.add(transaction)
        self.db_session.flush()

        return transaction

    def get_by_source_reference(
        self,
        user_id: int,
        source_reference: str,
    ) -> PortfolioTransaction | None:

        statement = select(
            PortfolioTransaction
        ).where(
            PortfolioTransaction.user_id == user_id,
            PortfolioTransaction.source_reference
            == source_reference,
        )

        return self.db_session.execute(
            statement
        ).scalar_one_or_none()

    def get_by_user(
        self,
        user_id: int,
    ) -> list[PortfolioTransaction]:

        statement = (
            select(PortfolioTransaction)
            .where(
                PortfolioTransaction.user_id
                == user_id,
            )
            .order_by(
                PortfolioTransaction.transaction_date,
                PortfolioTransaction.id,
            )
        )

        return list(
            self.db_session.execute(
                statement
            ).scalars()
        )
