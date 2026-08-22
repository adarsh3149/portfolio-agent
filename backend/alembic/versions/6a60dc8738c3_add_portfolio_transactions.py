"""add portfolio transactions

Revision ID: 6a60dc8738c3
Revises: b79071662766
Create Date: 2026-08-22 06:35:01.919447

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6a60dc8738c3"
down_revision: Union[str, Sequence[str], None] = "b79071662766"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "portfolio_transactions",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "isin",
            sa.String(length=12),
            nullable=False,
        ),
        sa.Column(
            "security_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "transaction_date",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "transaction_type",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "quantity",
            sa.Numeric(
                precision=20,
                scale=6,
            ),
            nullable=False,
        ),
        sa.Column(
            "source",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "source_reference",
            sa.String(length=255),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source_reference",
            name="uq_portfolio_transactions_source_reference",
        ),
    )

    op.create_index(
        "ix_portfolio_transactions_user_id",
        "portfolio_transactions",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_portfolio_transactions_isin",
        "portfolio_transactions",
        ["isin"],
        unique=False,
    )

    op.create_index(
        "ix_portfolio_transactions_source_reference",
        "portfolio_transactions",
        ["source_reference"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_portfolio_transactions_source_reference",
        table_name="portfolio_transactions",
    )

    op.drop_index(
        "ix_portfolio_transactions_isin",
        table_name="portfolio_transactions",
    )

    op.drop_index(
        "ix_portfolio_transactions_user_id",
        table_name="portfolio_transactions",
    )

    op.drop_table(
        "portfolio_transactions",
    )