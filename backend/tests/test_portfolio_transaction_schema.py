from datetime import date
from decimal import Decimal

from app.schemas.portfolio import (
    PortfolioTransaction,
    PortfolioTransactionType,
)


def test_create_buy_transaction():

    transaction = PortfolioTransaction(
        isin="INF843K01AO4",
        security_name="EDELWEISS MID CAP FUND",
        transaction_date=date(2026, 7, 1),
        transaction_type=PortfolioTransactionType.BUY,
        quantity=Decimal("0.790"),
        source="CDSL",
        source_reference="cdsl-cas-20260701-001",
    )

    assert transaction.isin == "INF843K01AO4"
    assert transaction.security_name == (
        "EDELWEISS MID CAP FUND"
    )
    assert transaction.transaction_date == date(
        2026,
        7,
        1,
    )
    assert transaction.transaction_type == (
        PortfolioTransactionType.BUY
    )
    assert transaction.quantity == Decimal(
        "0.790"
    )
    assert transaction.source == "CDSL"
    assert transaction.source_reference == (
        "cdsl-cas-20260701-001"
    )


def test_transaction_types_are_available():

    assert PortfolioTransactionType.BUY.value == "BUY"
    assert PortfolioTransactionType.SELL.value == "SELL"
    assert PortfolioTransactionType.DIVIDEND.value == "DIVIDEND"
    assert PortfolioTransactionType.BONUS.value == "BONUS"
    assert PortfolioTransactionType.SPLIT.value == "SPLIT"
    assert PortfolioTransactionType.TRANSFER.value == "TRANSFER"
    assert PortfolioTransactionType.REDEMPTION.value == "REDEMPTION"
    assert PortfolioTransactionType.ALLOTMENT.value == "ALLOTMENT"
    assert PortfolioTransactionType.OTHER.value == "OTHER"


def test_zero_quantity_is_supported():

    transaction = PortfolioTransaction(
        isin="INF843K01AO4",
        security_name="TEST SECURITY",
        transaction_date=date(2026, 7, 1),
        transaction_type=PortfolioTransactionType.OTHER,
        quantity=Decimal("0"),
        source="CDSL",
        source_reference="test-reference",
    )

    assert transaction.quantity == Decimal("0")
