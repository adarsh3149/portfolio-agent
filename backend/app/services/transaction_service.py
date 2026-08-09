from decimal import Decimal

from fastapi import HTTPException, status

from app.models.transaction import Transaction
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionCreate
from app.repositories.asset_repository import AssetRepository


class TransactionService:

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        asset_repository: AssetRepository,
    ):
        self.transaction_repository = transaction_repository
        self.asset_repository = asset_repository

    def create_transaction(
        self,
        user_id: int,
        request: TransactionCreate,
    ) -> Transaction:

        asset = self.asset_repository.get_by_id(
            request.asset_id
        )

        if asset is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found",
            )

        if request.quantity <= Decimal("0"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than zero.",
            )

        if request.price <= Decimal("0"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Price must be greater than zero.",
            )

        amount = request.quantity * request.price

        transaction = Transaction(
            user_id=user_id,
            asset_id=request.asset_id,
            transaction_type=request.transaction_type,
            quantity=request.quantity,
            price=request.price,
            amount=amount,
            charges=request.charges,
            transaction_date=request.transaction_date,
            notes=request.notes,
        )

        return self.transaction_repository.create(
            transaction
        )