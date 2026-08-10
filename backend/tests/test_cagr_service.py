from datetime import date
from decimal import Decimal

import pytest

from app.services.cagr_service import CAGRService


def test_cagr_for_one_year():
    service = CAGRService()

    result = service.calculate(
        initial_value=Decimal("100000"),
        final_value=Decimal("110000"),
        start_date=date(2025, 8, 10),
        end_date=date(2026, 8, 10),
    )

    assert result == Decimal("0.10")


def test_cagr_for_multiple_years():
    service = CAGRService()

    result = service.calculate(
        initial_value=Decimal("100000"),
        final_value=Decimal("121000"),
        start_date=date(2024, 8, 10),
        end_date=date(2026, 8, 10),
    )

    assert result == Decimal("0.10")


def test_cagr_returns_zero_when_values_are_equal():
    service = CAGRService()

    result = service.calculate(
        initial_value=Decimal("100000"),
        final_value=Decimal("100000"),
        start_date=date(2025, 8, 10),
        end_date=date(2026, 8, 10),
    )

    assert result == Decimal("0")


def test_cagr_rejects_zero_initial_value():
    service = CAGRService()

    with pytest.raises(
        ValueError,
        match="Initial value must be greater than zero.",
    ):
        service.calculate(
            initial_value=Decimal("0"),
            final_value=Decimal("100000"),
            start_date=date(2025, 8, 10),
            end_date=date(2026, 8, 10),
        )


def test_cagr_rejects_negative_initial_value():
    service = CAGRService()

    with pytest.raises(
        ValueError,
        match="Initial value must be greater than zero.",
    ):
        service.calculate(
            initial_value=Decimal("-100"),
            final_value=Decimal("100000"),
            start_date=date(2025, 8, 10),
            end_date=date(2026, 8, 10),
        )


def test_cagr_rejects_end_date_before_start_date():
    service = CAGRService()

    with pytest.raises(
        ValueError,
        match="End date must be after start date.",
    ):
        service.calculate(
            initial_value=Decimal("100000"),
            final_value=Decimal("110000"),
            start_date=date(2026, 8, 10),
            end_date=date(2025, 8, 10),
        )


def test_cagr_rejects_same_start_and_end_date():
    service = CAGRService()

    with pytest.raises(
        ValueError,
        match="End date must be after start date.",
    ):
        service.calculate(
            initial_value=Decimal("100000"),
            final_value=Decimal("110000"),
            start_date=date(2026, 8, 10),
            end_date=date(2026, 8, 10),
        )
