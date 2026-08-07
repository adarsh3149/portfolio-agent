from datetime import UTC, datetime

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.enums import AssetType
from app.enums import Currency
from app.enums import Exchange


class Asset(Base):
    __tablename__ = "assets"

    __table_args__ = (
        UniqueConstraint(
            "exchange",
            "symbol",
            name="uq_exchange_symbol",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    symbol: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    asset_type: Mapped[AssetType] = mapped_column(
        SqlEnum(AssetType),
        nullable=False,
    )

    exchange: Mapped[Exchange] = mapped_column(
        SqlEnum(Exchange),
        nullable=False,
    )

    currency: Mapped[Currency] = mapped_column(
        SqlEnum(Currency),
        nullable=False,
    )

    isin: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
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

    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="asset",
    )