"""add market price table

Revision ID: 175f65b2a92f
Revises: 492412835007
Create Date: 2026-08-09 08:01:27.488539

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "175f65b2a92f"
down_revision: Union[str, Sequence[str], None] = "492412835007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "market_prices",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "asset_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "price",
            sa.Numeric(
                precision=20,
                scale=4,
            ),
            nullable=False,
        ),
        sa.Column(
            "source",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "price_time",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["asset_id"],
            ["assets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_market_prices_asset_id"),
        "market_prices",
        ["asset_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_market_prices_price_time"),
        "market_prices",
        ["price_time"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_market_prices_price_time"),
        table_name="market_prices",
    )

    op.drop_index(
        op.f("ix_market_prices_asset_id"),
        table_name="market_prices",
    )

    op.drop_table("market_prices")