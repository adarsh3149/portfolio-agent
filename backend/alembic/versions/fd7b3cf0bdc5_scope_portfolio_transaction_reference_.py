"""scope portfolio transaction reference by user

Revision ID: fd7b3cf0bdc5
Revises: 6a60dc8738c3
Create Date: 2026-08-22 06:52:13.053827

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "fd7b3cf0bdc5"
down_revision: Union[str, Sequence[str], None] = "6a60dc8738c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.drop_constraint(
        "uq_portfolio_transactions_source_reference",
        "portfolio_transactions",
        type_="unique",
    )

    op.create_unique_constraint(
        "uq_portfolio_transactions_user_source_reference",
        "portfolio_transactions",
        ["user_id", "source_reference"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "uq_portfolio_transactions_user_source_reference",
        "portfolio_transactions",
        type_="unique",
    )

    op.create_unique_constraint(
        "uq_portfolio_transactions_source_reference",
        "portfolio_transactions",
        ["source_reference"],
    )