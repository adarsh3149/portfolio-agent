from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database_types import Money
from app.database.base import Base


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "snapshot_date",
            name="uq_portfolio_snapshot_user_date",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    snapshot_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    total_invested: Mapped[Decimal] = mapped_column(
        Money,
        nullable=False,
    )

    total_market_value: Mapped[Decimal] = mapped_column(
        Money,
        nullable=False,
    )

    total_realized_profit_loss: Mapped[Decimal] = mapped_column(
        Money,
        nullable=False,
    )

    total_unrealized_profit_loss: Mapped[Decimal] = mapped_column(
        Money,
        nullable=False,
    )

    total_profit_loss: Mapped[Decimal] = mapped_column(
        Money,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="portfolio_snapshots",
    )
