from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Date,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class PortfolioTransaction(Base):
    __tablename__ = "portfolio_transactions"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "source_reference",
            name="uq_portfolio_transactions_user_source_reference",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    isin: Mapped[str] = mapped_column(
        String(12),
        nullable=False,
        index=True,
    )

    security_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    transaction_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    transaction_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 6),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    source_reference: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )