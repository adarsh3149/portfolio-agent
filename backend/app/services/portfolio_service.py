from decimal import Decimal

from app.repositories.transaction_repository import TransactionRepository
from app.schemas.portfolio import PortfolioSummary
from app.services.holding_service import HoldingService

class PortfolioService:

    def __init__(
        self,
        holding_service: HoldingService,
        transaction_repository: TransactionRepository,
    ):
        self.holding_service = holding_service
        self.transaction_repository = transaction_repository

    def get_summary(
            self,
            user_id: int,
    ) -> PortfolioSummary:

        holdings = self.holding_service.get_holdings(user_id)

        total_invested = sum(
            (holding.invested_amount for holding in holdings),
            start=Decimal("0.00"),
        )

        total_transactions = (
            self.transaction_repository.count_by_user(
                user_id
            )
        )

        return PortfolioSummary(
            total_holdings=len(holdings),
            total_transactions=total_transactions,
            total_invested=total_invested,
        )