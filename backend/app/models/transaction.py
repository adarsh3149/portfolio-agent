from datetime import UTC, date, datetime
from decimal import Decimal
from sqlalchemy.orm import relationship

from app.models.asset import Asset
from app.models.user import User

from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.core.database_types import Money, Price, Quantity
from app.database.base import Base
from app.enums import TransactionType

from sqlalchemy.orm import Mapped, mapped_column, relationship

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    user_id = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id"),
        nullable=False,
        index=True
    )

    transaction_type: Mapped[TransactionType] = mapped_column(
        SqlEnum(
            TransactionType,
            name="transaction_type_enum",
        ),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Quantity,
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        Price,
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Money,
        nullable=False,
    )

    charges: Mapped[Decimal] = mapped_column(
        Money,
        default=Decimal("0.00"),
        nullable=False,
    )

    transaction_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    notes: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="transactions",
    )

    asset: Mapped["Asset"] = relationship(
        back_populates="transactions",
    )