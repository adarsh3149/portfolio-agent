from datetime import date
from decimal import Decimal

from app.schemas.cdsl import (
    CDSLCASTransaction,
)
from app.services.cdsl.transaction_normalizer import (
    CDSLTransactionNormalizer,
)


def test_normalize_purchase_transaction():

    normalizer = CDSLTransactionNormalizer()

    transaction = CDSLCASTransaction(
        isin="INF843K01AO4",
        security_name="EDELWEISS MID CAP FUND",
        transaction_particulars="PURCHASE",
        transaction_date=date(2026, 7, 1),
        opening_balance=Decimal("85.907"),
        credit=Decimal("0.790"),
        debit=Decimal("0"),
        closing_balance=Decimal("86.697"),
        stamp_duty=Decimal("0"),
    )

    result = normalizer.normalize(
        transaction,
    )

    assert result.isin == "INF843K01AO4"
    assert result.security_name == (
        "EDELWEISS MID CAP FUND"
    )
    assert result.transaction_date == date(
        2026,
        7,
        1,
    )
    assert result.quantity == Decimal(
        "0.790"
    )
    assert result.source == "CDSL"
    assert result.transaction_type.value == "BUY"


def test_normalize_redemption_transaction():

    normalizer = CDSLTransactionNormalizer()

    transaction = CDSLCASTransaction(
        isin="INF843K01AO4",
        security_name="EDELWEISS MID CAP FUND",
        transaction_particulars="REDEMPTION",
        transaction_date=date(2026, 7, 10),
        opening_balance=Decimal("86.697"),
        credit=Decimal("0"),
        debit=Decimal("1.000"),
        closing_balance=Decimal("85.697"),
        stamp_duty=Decimal("0"),
    )

    result = normalizer.normalize(
        transaction,
    )

    assert result.transaction_type.value == "REDEMPTION"
    assert result.quantity == Decimal(
        "1.000"
    )


def test_normalize_dividend_transaction():

    normalizer = CDSLTransactionNormalizer()

    transaction = CDSLCASTransaction(
        isin="INF843K01AO4",
        security_name="EDELWEISS MID CAP FUND",
        transaction_particulars="DIVIDEND",
        transaction_date=date(2026, 7, 15),
        opening_balance=Decimal("85.697"),
        credit=Decimal("0"),
        debit=Decimal("0"),
        closing_balance=Decimal("85.697"),
        stamp_duty=Decimal("0"),
    )

    result = normalizer.normalize(
        transaction,
    )

    assert result.transaction_type.value == "DIVIDEND"
    assert result.quantity == Decimal("0")


def test_normalize_unknown_transaction():

    normalizer = CDSLTransactionNormalizer()

    transaction = CDSLCASTransaction(
        isin="INF843K01AO4",
        security_name="EDELWEISS MID CAP FUND",
        transaction_particulars="SOME UNKNOWN CDSL EVENT",
        transaction_date=date(2026, 7, 20),
        opening_balance=Decimal("85.697"),
        credit=Decimal("1.000"),
        debit=Decimal("0"),
        closing_balance=Decimal("86.697"),
        stamp_duty=Decimal("0"),
    )

    result = normalizer.normalize(
        transaction,
    )

    assert result.transaction_type.value == "OTHER"
    assert result.quantity == Decimal(
        "1.000"
    )
    
def test_source_reference_is_deterministic():

    normalizer = CDSLTransactionNormalizer()

    transaction = CDSLCASTransaction(
        isin="INF843K01AO4",
        security_name="EDELWEISS MID CAP FUND",
        transaction_particulars="PURCHASE",
        transaction_date=date(2026, 7, 1),
        opening_balance=Decimal("85.907"),
        credit=Decimal("0.790"),
        debit=Decimal("0"),
        closing_balance=Decimal("86.697"),
        stamp_duty=Decimal("0"),
    )

    result_1 = normalizer.normalize(transaction)
    result_2 = normalizer.normalize(transaction)

    assert result_1.source_reference == result_2.source_reference


def test_different_transactions_have_different_source_references():

    normalizer = CDSLTransactionNormalizer()

    transaction_1 = CDSLCASTransaction(
        isin="INF843K01AO4",
        security_name="EDELWEISS MID CAP FUND",
        transaction_particulars="PURCHASE",
        transaction_date=date(2026, 7, 1),
        opening_balance=Decimal("85.907"),
        credit=Decimal("0.790"),
        debit=Decimal("0"),
        closing_balance=Decimal("86.697"),
        stamp_duty=Decimal("0"),
    )

    transaction_2 = CDSLCASTransaction(
        isin="INF843K01AO4",
        security_name="EDELWEISS MID CAP FUND",
        transaction_particulars="PURCHASE",
        transaction_date=date(2026, 7, 2),
        opening_balance=Decimal("86.697"),
        credit=Decimal("0.788"),
        debit=Decimal("0"),
        closing_balance=Decimal("87.485"),
        stamp_duty=Decimal("0"),
    )

    result_1 = normalizer.normalize(transaction_1)
    result_2 = normalizer.normalize(transaction_2)

    assert result_1.source_reference != result_2.source_reference
