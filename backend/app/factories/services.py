from sqlalchemy.orm import Session

from app.repositories.market_price_repository import (
    MarketPriceRepository,
)
from app.repositories.transaction_repository import (
    TransactionRepository,
)
from app.services.holding_service import HoldingService
from app.services.performance_service import PerformanceService
from app.services.portfolio_performance_service import (
    PortfolioPerformanceService,
)


def create_portfolio_performance_service(
    db: Session,
) -> PortfolioPerformanceService:

    transaction_repository = TransactionRepository(
        db
    )

    market_price_repository = MarketPriceRepository(
        db
    )

    holding_service = HoldingService(
        transaction_repository
    )

    performance_service = PerformanceService(
        repository=transaction_repository,
    )

    return PortfolioPerformanceService(
        holding_service=holding_service,
        performance_service=performance_service,
        market_price_repository=market_price_repository,
    )
