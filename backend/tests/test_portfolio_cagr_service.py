from datetime import date
from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.services.portfolio_cagr_service import (
    PortfolioCAGRService,
)


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


def test_portfolio_cagr_uses_first_and_last_snapshots():
    repository = Mock()

    repository.get_by_user.return_value = [
        make_snapshot(
            date(2024, 8, 10),
            "100000",
        ),
        make_snapshot(
            date(2025, 8, 10),
            "110000",
        ),
        make_snapshot(
            date(2026, 8, 10),
            "121000",
        ),
    ]

    service = PortfolioCAGRService(
        repository=repository,
    )

    result = service.calculate(
        user_id=1,
    )

    assert result == Decimal("0.10")

    repository.get_by_user.assert_called_once_with(
        user_id=1,
        start_date=None,
        end_date=None,
    )


def test_portfolio_cagr_supports_date_range():
    repository = Mock()

    repository.get_by_user.return_value = [
        make_snapshot(
            date(2024, 8, 10),
            "100000",
        ),
        make_snapshot(
            date(2025, 8, 10),
            "110000",
        ),
        make_snapshot(
            date(2026, 8, 10),
            "121000",
        ),
    ]

    service = PortfolioCAGRService(
        repository=repository,
    )

    result = service.calculate(
        user_id=1,
        start_date=date(2024, 8, 10),
        end_date=date(2026, 8, 10),
    )

    assert result == Decimal("0.10")

    repository.get_by_user.assert_called_once_with(
        user_id=1,
        start_date=date(2024, 8, 10),
        end_date=date(2026, 8, 10),
    )


def test_portfolio_cagr_requires_at_least_two_snapshots():
    repository = Mock()

    repository.get_by_user.return_value = [
        make_snapshot(
            date(2026, 8, 10),
            "100000",
        ),
    ]

    service = PortfolioCAGRService(
        repository=repository,
    )

    with pytest.raises(
        ValueError,
        match="At least two portfolio snapshots are required.",
    ):
        service.calculate(
            user_id=1,
        )


def test_portfolio_cagr_requires_snapshots():
    repository = Mock()

    repository.get_by_user.return_value = []

    service = PortfolioCAGRService(
        repository=repository,
    )

    with pytest.raises(
        ValueError,
        match="At least two portfolio snapshots are required.",
    ):
        service.calculate(
            user_id=1,
        )


def test_portfolio_cagr_uses_market_value_not_invested_value():
    repository = Mock()

    first = make_snapshot(
        date(2025, 8, 10),
        "100000",
    )
    first.total_invested = Decimal("90000")

    second = make_snapshot(
        date(2026, 8, 10),
        "120000",
    )
    second.total_invested = Decimal("110000")

    repository.get_by_user.return_value = [
        first,
        second,
    ]

    service = PortfolioCAGRService(
        repository=repository,
    )

    result = service.calculate(
        user_id=1,
    )

    assert result == Decimal("0.20")
