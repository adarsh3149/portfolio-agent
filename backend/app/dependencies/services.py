from fastapi import Depends

from app.dependencies.repositories import (
    get_transaction_repository,
     get_asset_repository,
    get_user_repository,
)
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.holding_service import HoldingService
from app.repositories.asset_repository import AssetRepository
from app.services.transaction_service import TransactionService
from app.dependencies.repositories import get_asset_repository
from app.repositories.asset_repository import AssetRepository
from app.services.asset_service import AssetService
from app.services.portfolio_service import PortfolioService


def get_auth_service(
    repository: UserRepository = Depends(get_user_repository),
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