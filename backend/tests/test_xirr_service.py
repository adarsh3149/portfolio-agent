from datetime import date
from decimal import Decimal

import pytest

from app.services.xirr_service import XIRRService


def test_xirr_for_simple_one_year_investment():
    service = XIRRService()

    result = service.calculate(
        cash_flows=[
            (date(2025, 8, 10), Decimal("-100000")),
            (date(2026, 8, 10), Decimal("110000")),
        ],
    )

    assert float(result) == pytest.approx(
        0.10,
        abs=0.0001,
    )


def test_xirr_handles_irregular_cash_flows():
    service = XIRRService()

    result = service.calculate(
        cash_flows=[
            (date(2025, 1, 1), Decimal("-10000")),
            (date(2025, 3, 15), Decimal("-5000")),
            (date(2025, 7, 20), Decimal("-3000")),
            (date(2026, 1, 1), Decimal("21000")),
        ],
    )

    assert float(result) == pytest.approx(
        0.197157,
        abs=0.0005,
    )


def test_xirr_supports_negative_return():
    service = XIRRService()

    result = service.calculate(
        cash_flows=[
            (date(2025, 8, 10), Decimal("-100000")),
            (date(2026, 8, 10), Decimal("90000")),
        ],
    )

    assert float(result) == pytest.approx(
        -0.10,
        abs=0.0001,
    )


def test_xirr_requires_positive_and_negative_cash_flows():
    service = XIRRService()

    with pytest.raises(
        ValueError,
        match="Cash flows must contain both positive and negative values.",
    ):
        service.calculate(
            cash_flows=[
                (date(2025, 8, 10), Decimal("-100000")),
                (date(2026, 8, 10), Decimal("-5000")),
            ],
        )


def test_xirr_requires_at_least_two_cash_flows():
    service = XIRRService()

    with pytest.raises(
        ValueError,
        match="At least two cash flows are required.",
    ):
        service.calculate(
            cash_flows=[
                (date(2025, 8, 10), Decimal("-100000")),
            ],
        )


def test_xirr_rejects_duplicate_dates_with_only_zero_net_flow():
    service = XIRRService()

    with pytest.raises(
        ValueError,
        match="Cash flows must contain both positive and negative values.",
    ):
        service.calculate(
            cash_flows=[
                (date(2025, 8, 10), Decimal("-100000")),
                (date(2025, 8, 10), Decimal("0")),
            ],
        )


def test_xirr_rejects_zero_cash_flow_only():
    service = XIRRService()

    with pytest.raises(
        ValueError,
        match="Cash flows must contain both positive and negative values.",
    ):
        service.calculate(
            cash_flows=[
                (date(2025, 8, 10), Decimal("0")),
                (date(2026, 8, 10), Decimal("0")),
            ],
        )

def test_xirr_returns_zero_for_equal_cash_flows():
    service = XIRRService()

    result = service.calculate(
        cash_flows=[
            (date(2025, 8, 10), Decimal("-100000")),
            (date(2025, 8, 11), Decimal("100000")),
        ],
    )

    assert float(result) == pytest.approx(
        0,
        abs=0.0001,
    )