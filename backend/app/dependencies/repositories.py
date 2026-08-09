from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.repositories.asset_repository import AssetRepository
from app.repositories.market_price_repository import MarketPriceRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.user_repository import UserRepository


def get_user_repository(
    db: Session = Depends(get_db),
) -> UserRepository:
    return UserRepository(db)


def get_asset_repository(
    db: Session = Depends(get_db),
) -> AssetRepository:
    return AssetRepository(db)


def get_transaction_repository(
    db: Session = Depends(get_db),
) -> TransactionRepository:
    return TransactionRepository(db)


def get_market_price_repository(
    db: Session = Depends(get_db),
) -> MarketPriceRepository:
    return MarketPriceRepository(db)