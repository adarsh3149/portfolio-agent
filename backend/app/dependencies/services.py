from fastapi import Depends
from decimal import Decimal

from app.dependencies.repositories import (
    get_asset_repository,
    get_market_price_repository,
    get_transaction_repository,
    get_user_repository,
)
from app.repositories.asset_repository import AssetRepository
from app.repositories.market_price_repository import MarketPriceRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.services.asset_service import AssetService
from app.services.auth_service import AuthService
from app.services.fake_market_data_provider import (
    FakeMarketDataProvider,
)
from app.services.holding_service import HoldingService
from app.services.market_data_provider import MarketDataProvider
from app.services.market_data_service import MarketDataService
from app.services.portfolio_service import PortfolioService
from app.services.transaction_service import TransactionService

from app.services.portfolio_valuation_service import (
    PortfolioValuationService,
)

from app.services.performance_service import PerformanceService
from app.services.portfolio_performance_service import (
    PortfolioPerformanceService,
)


def get_auth_service(
    repository: UserRepository = Depends(
        get_user_repository,
    ),
) -> AuthService:

    return AuthService(repository)


def get_holding_service(
    repository: TransactionRepository = Depends(
        get_transaction_repository,
    ),
) -> HoldingService:

    return HoldingService(
        repository,
    )


def get_transaction_service(
    transaction_repository: TransactionRepository = Depends(
        get_transaction_repository,
    ),
    asset_repository: AssetRepository = Depends(
        get_asset_repository,
    ),
) -> TransactionService:

    return TransactionService(
        transaction_repository=transaction_repository,
        asset_repository=asset_repository,
    )


def get_asset_service(
    repository: AssetRepository = Depends(
        get_asset_repository,
    ),
) -> AssetService:

    return AssetService(repository)


def get_portfolio_service(
    holding_service: HoldingService = Depends(
        get_holding_service,
    ),
    transaction_repository: TransactionRepository = Depends(
        get_transaction_repository,
    ),
) -> PortfolioService:

    return PortfolioService(
        holding_service=holding_service,
        transaction_repository=transaction_repository,
    )


def get_market_data_provider() -> MarketDataProvider:

    return FakeMarketDataProvider(
        {
            "INFY": Decimal("1450.25"),
        }
    )


def get_market_data_service(
    asset_repository: AssetRepository = Depends(
        get_asset_repository,
    ),
    market_price_repository: MarketPriceRepository = Depends(
        get_market_price_repository,
    ),
    provider: MarketDataProvider = Depends(
        get_market_data_provider,
    ),
) -> MarketDataService:

    return MarketDataService(
        asset_repository=asset_repository,
        market_price_repository=market_price_repository,
        provider=provider,
    )

def get_portfolio_valuation_service(
    holding_service: HoldingService = Depends(
        get_holding_service,
    ),
    market_price_repository: MarketPriceRepository = Depends(
        get_market_price_repository,
    ),
) -> PortfolioValuationService:

    return PortfolioValuationService(
        holding_service=holding_service,
        market_price_repository=market_price_repository,
    )

def get_performance_service(
    transaction_repository: TransactionRepository = Depends(
        get_transaction_repository,
    ),
) -> PerformanceService:

    return PerformanceService(
        repository=transaction_repository,
    )


def get_portfolio_performance_service(
    holding_service: HoldingService = Depends(
        get_holding_service,
    ),
    performance_service: PerformanceService = Depends(
        get_performance_service,
    ),
    market_price_repository: MarketPriceRepository = Depends(
        get_market_price_repository,
    ),
) -> PortfolioPerformanceService:

    return PortfolioPerformanceService(
        holding_service=holding_service,
        performance_service=performance_service,
        market_price_repository=market_price_repository,
    )