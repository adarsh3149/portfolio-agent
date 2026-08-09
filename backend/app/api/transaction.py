from fastapi import APIRouter, Depends, status

from app.dependencies.auth import get_current_user
from app.dependencies.services import get_transaction_service
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
)
from app.services.transaction_service import TransactionService

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)

@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    request: TransactionCreate,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(
        get_transaction_service,
    ),
):
    return service.create_transaction(
        user_id=current_user.id,
        request=request,
    )