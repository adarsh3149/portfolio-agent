from datetime import date
from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.enums import TransactionType
from app.services.portfolio_xirr_service import (
    PortfolioXIRRService,
)


def make_transaction(
    transaction_type: TransactionType,
    transaction_date: date,
    amount: str,
    charges: str = "0",
):
    transaction = Mock()

    transaction.transaction_type = transaction_type
    transaction.transaction_date = transaction_date
    transaction.amount = Decimal(amount)
    transaction.charges = Decimal(charges)

    return transaction


def make_snapshot(
    snapshot_date: date,
    market_value: str,
):
    snapshot = Mock()

    snapshot.snapshot_date = snapshot_date
    snapshot.total_market_value = Decimal(
        market_value
    )

    return snapshot


def test_portfolio_xirr_uses_transactions_and_final_value():
    transaction_repository = Mock()
    snapshot_repository = Mock()

    transaction_repository.get_by_user.return_value = [
        make_transaction(
            TransactionType.BUY,
            date(2025, 8, 10),
            "100000",
            "20",
        ),
    ]

    snapshot_repository.get_by_user.return_value = [
        make_snapshot(
            date(2026, 8, 10),
            "110000",
        ),
    ]

    service = PortfolioXIRRService(
        transaction_repository=transaction_repository,
        snapshot_repository=snapshot_repository,
    )

    result = service.calculate(
        user_id=1,
    )

    assert float(result) == pytest.approx(
        0.099780,
        abs=0.0001,
    )


def test_portfolio_xirr_includes_sell_transactions():
    transaction_repository = Mock()
    snapshot_repository = Mock()

    transaction_repository.get_by_user.return_value = [
        make_transaction(
            TransactionType.BUY,
            date(2025, 1, 1),
            "100000",
            "20",
        ),
        make_transaction(
            TransactionType.SELL,
            date(2025, 7, 1),
            "30000",
            "10",
        ),
    ]

    snapshot_repository.get_by_user.return_value = [
        make_snapshot(
            date(2026, 1, 1),
            "80000",
        ),
    ]

    service = PortfolioXIRRService(
        transaction_repository=transaction_repository,
        snapshot_repository=snapshot_repository,
    )

    result = service.calculate(
        user_id=1,
    )

    assert result is not None

    transaction_repository.get_by_user.assert_called_once_with(
        user_id=1,
    )


def test_portfolio_xirr_uses_charges_in_cash_flows():
    transaction_repository = Mock()
    snapshot_repository = Mock()

    transaction_repository.get_by_user.return_value = [
        make_transaction(
            TransactionType.BUY,
            date(2025, 8, 10),
            "100000",
            "100",
        ),
    ]

    snapshot_repository.get_by_user.return_value = [
        make_snapshot(
            date(2026, 8, 10),
            "110000",
        ),
    ]

    service = PortfolioXIRRService(
        transaction_repository=transaction_repository,
        snapshot_repository=snapshot_repository,
    )

    result = service.calculate(
        user_id=1,
    )

    # Investing 100,100 and receiving 110,000
    # gives a return slightly below 10%.
    assert float(result) < 0.10


def test_portfolio_xirr_requires_transactions():
    transaction_repository = Mock()
    snapshot_repository = Mock()

    transaction_repository.get_by_user.return_value = []

    service = PortfolioXIRRService(
        transaction_repository=transaction_repository,
        snapshot_repository=snapshot_repository,
    )

    with pytest.raises(
        ValueError,
        match="At least one transaction is required.",
    ):
        service.calculate(
            user_id=1,
        )


def test_portfolio_xirr_requires_final_snapshot():
    transaction_repository = Mock()
    snapshot_repository = Mock()

    transaction_repository.get_by_user.return_value = [
        make_transaction(
            TransactionType.BUY,
            date(2025, 8, 10),
            "100000",
        ),
    ]

    snapshot_repository.get_by_user.return_value = []

    service = PortfolioXIRRService(
        transaction_repository=transaction_repository,
        snapshot_repository=snapshot_repository,
    )

    with pytest.raises(
        ValueError,
        match="A portfolio snapshot is required.",
    ):
        service.calculate(
            user_id=1,
        )


def test_portfolio_xirr_uses_latest_snapshot():
    transaction_repository = Mock()
    snapshot_repository = Mock()

    transaction_repository.get_by_user.return_value = [
        make_transaction(
            TransactionType.BUY,
            date(2025, 1, 1),
            "100000",
        ),
    ]

    snapshot_repository.get_by_user.return_value = [
        make_snapshot(
            date(2025, 6, 1),
            "105000",
        ),
        make_snapshot(
            date(2026, 1, 1),
            "110000",
        ),
    ]

    service = PortfolioXIRRService(
        transaction_repository=transaction_repository,
        snapshot_repository=snapshot_repository,
    )

    result = service.calculate(
        user_id=1,
    )

    assert float(result) == pytest.approx(
        0.10,
        abs=0.0001,
    )


def test_portfolio_xirr_supports_date_range():
    transaction_repository = Mock()
    snapshot_repository = Mock()

    transaction_repository.get_by_user.return_value = [
        make_transaction(
            TransactionType.BUY,
            date(2024, 1, 1),
            "100000",
        ),
        make_transaction(
            TransactionType.BUY,
            date(2025, 1, 1),
            "10000",
        ),
    ]

    snapshot_repository.get_by_user.return_value = [
        make_snapshot(
            date(2025, 1, 1),
            "110000",
        ),
        make_snapshot(
            date(2026, 1, 1),
            "125000",
        ),
    ]

    service = PortfolioXIRRService(
        transaction_repository=transaction_repository,
        snapshot_repository=snapshot_repository,
    )

    result = service.calculate(
        user_id=1,
        start_date=date(2025, 1, 1),
        end_date=date(2026, 1, 1),
    )

    assert result is not None

    snapshot_repository.get_by_user.assert_called_once_with(
        user_id=1,
        start_date=date(2025, 1, 1),
        end_date=date(2026, 1, 1),
    )
