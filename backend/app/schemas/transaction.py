from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.enums import TransactionType


class TransactionCreate(BaseModel):
    asset_id: int
    transaction_type: TransactionType

    quantity: Decimal
    price: Decimal
    charges: Decimal = Decimal("0.00")

    transaction_date: date
    notes: str | None = None


class TransactionResponse(BaseModel):
    id: int

    asset_id: int
    transaction_type: TransactionType

    quantity: Decimal
    price: Decimal
    amount: Decimal
    charges: Decimal

    transaction_date: date
    notes: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )