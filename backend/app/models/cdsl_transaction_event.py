from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database_types import Quantity
from app.database.base import Base
from app.schemas.cdsl import CDSLTransactionDirection


class CDSLTransactionEvent(Base):
    __tablename__ = "cdsl_transaction_events"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "source",
            "source_reference",
            name="uq_cdsl_event_source_reference",
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

    security_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    isin: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Quantity,
        nullable=False,
    )

    direction: Mapped[CDSLTransactionDirection] = mapped_column(
        SqlEnum(
            CDSLTransactionDirection,
            name="cdsl_transaction_direction",
        ),
        nullable=False,
    )

    transaction_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="CDSL",
    )

    source_reference: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    processed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
