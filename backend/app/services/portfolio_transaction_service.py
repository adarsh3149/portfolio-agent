from sqlalchemy.orm import Session

from app.repositories.portfolio_transaction_repository import (
    PortfolioTransactionRepository,
)
from app.schemas.cdsl import CDSLCASTransaction
from app.schemas.portfolio import PortfolioTransaction
from app.services.cdsl.transaction_normalizer import (
    CDSLTransactionNormalizer,
)


class PortfolioTransactionService:

    def __init__(
        self,
        db_session: Session,
    ):
        self.repository = (
            PortfolioTransactionRepository(
                db_session,
            )
        )

        self.normalizer = (
            CDSLTransactionNormalizer()
        )

    def import_transaction(
        self,
        user_id: int,
        transaction: CDSLCASTransaction,
    ) -> PortfolioTransaction:

        normalized = self.normalizer.normalize(
            transaction,
        )

        existing = (
            self.repository.get_by_source_reference(
                user_id=user_id,
                source_reference=(
                    normalized.source_reference
                ),
            )
        )

        if existing is not None:
            return existing

        return self.repository.create(
            user_id=user_id,
            isin=normalized.isin,
            security_name=normalized.security_name,
            transaction_date=(
                normalized.transaction_date
            ),
            transaction_type=(
                normalized.transaction_type.value
            ),
            quantity=normalized.quantity,
            source=normalized.source,
            source_reference=(
                normalized.source_reference
            ),
        )
