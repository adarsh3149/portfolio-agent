from datetime import date
from decimal import Decimal
from pathlib import Path

from app.services.cdsl.cas_transaction_parser import (
    CDSLCASNotFoundError,
    CDSLCasTransactionParser,
)


CAS_PDF = (
    Path(__file__).parent
    / "fixtures"
    / "cdsl"
    / "monthly_cas.pdf"
)


def test_parse_single_transaction():
    parser = CDSLCasTransactionParser()

    result = parser.parse(
        CAS_PDF,
    )

    assert len(result) > 0

    transaction = result[0]

    assert transaction.isin
    assert transaction.security_name
    assert transaction.transaction_particulars
    assert isinstance(
        transaction.transaction_date,
        date,
    )


def test_parse_transaction_balances():
    parser = CDSLCasTransactionParser()

    result = parser.parse(
        CAS_PDF,
    )

    transaction = result[0]

    assert isinstance(
        transaction.opening_balance,
        Decimal,
    )

    assert isinstance(
        transaction.credit,
        Decimal,
    )

    assert isinstance(
        transaction.debit,
        Decimal,
    )

    assert isinstance(
        transaction.closing_balance,
        Decimal,
    )


def test_parse_transaction_stamp_duty():
    parser = CDSLCasTransactionParser()

    result = parser.parse(
        CAS_PDF,
    )

    transaction = result[0]

    assert isinstance(
        transaction.stamp_duty,
        Decimal,
    )


def test_parse_multiple_transactions():
    parser = CDSLCasTransactionParser()

    result = parser.parse(
        CAS_PDF,
    )

    assert len(result) > 1


def test_parse_expected_cas_transactions():
    parser = CDSLCasTransactionParser()

    result = parser.parse(
        CAS_PDF,
    )

    isins = {
        transaction.isin
        for transaction in result
    }

    assert "INF179KA1RW5" in isins
    assert "INF843K01AO4" in isins


def test_parse_credit_transaction():
    parser = CDSLCasTransactionParser()

    result = parser.parse(
        CAS_PDF,
    )

    credit_transactions = [
        transaction
        for transaction in result
        if transaction.credit > Decimal("0")
    ]

    assert credit_transactions


def test_parse_missing_pdf():
    parser = CDSLCasTransactionParser()

    missing_pdf = (
        CAS_PDF.parent
        / "does_not_exist.pdf"
    )

    try:
        parser.parse(
            missing_pdf,
        )
        assert False
    except FileNotFoundError:
        pass
    
def test_parse_transaction_with_exact_values():
    parser = CDSLCasTransactionParser()

    result = parser.parse(
        CAS_PDF,
    )

    transactions = [
        transaction
        for transaction in result
        if transaction.isin == "INF843K01AO4"
        and transaction.transaction_date == date(2026, 7, 1)
    ]

    assert transactions

    transaction = transactions[0]

    assert transaction.security_name.startswith(
        "EDELWEISS"
    )

    assert transaction.opening_balance == Decimal(
        "85.907"
    )

    assert transaction.credit == Decimal(
        "0.790"
    )

    assert transaction.debit == Decimal(
        "0"
    )

    assert transaction.closing_balance == Decimal(
        "86.697"
    )

    assert transaction.stamp_duty == Decimal(
        "0"
    )


def test_parse_debit_and_credit_as_separate_values():
    parser = CDSLCasTransactionParser()

    result = parser.parse(
        CAS_PDF,
    )

    assert any(
        transaction.credit > Decimal("0")
        for transaction in result
    )

    assert all(
        transaction.credit >= Decimal("0")
        for transaction in result
    )

    assert all(
        transaction.debit >= Decimal("0")
        for transaction in result
    )


def test_parse_multiple_transactions_for_same_isin():
    parser = CDSLCasTransactionParser()

    result = parser.parse(
        CAS_PDF,
    )

    transactions = [
        transaction
        for transaction in result
        if transaction.isin == "INF843K01AO4"
    ]

    assert len(transactions) > 1


def test_transaction_dates_are_ordered_within_security():
    parser = CDSLCasTransactionParser()

    result = parser.parse(
        CAS_PDF,
    )

    transactions = [
        transaction
        for transaction in result
        if transaction.isin == "INF843K01AO4"
    ]

    dates = [
        transaction.transaction_date
        for transaction in transactions
    ]

    assert dates == sorted(dates)


def test_missing_credit_or_debit_is_zero():
    parser = CDSLCasTransactionParser()

    result = parser.parse(
        CAS_PDF,
    )

    for transaction in result:
        assert transaction.credit >= Decimal("0")
        assert transaction.debit >= Decimal("0")
