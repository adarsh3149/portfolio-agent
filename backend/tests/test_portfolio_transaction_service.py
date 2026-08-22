from datetime import date
from decimal import Decimal

from app.models.user import User
from app.schemas.cdsl import CDSLCASTransaction
from app.services.portfolio_transaction_service import (
    PortfolioTransactionService,
)

def create_user(
    db_session,
    email,
    name="Test User",
):
    user = User(
        name=name,
        email=email,
        password_hash="password",
    )

    db_session.add(user)
    db_session.commit()

    return user


def create_cas_transaction(
    *,
    isin="INF843K01AO4",
    security_name="EDELWEISS MID CAP FUND",
    transaction_particulars="PURCHASE",
    transaction_date=date(2026, 7, 1),
    opening_balance=Decimal("85.907"),
    credit=Decimal("0.790"),
    debit=Decimal("0"),
    closing_balance=Decimal("86.697"),
    stamp_duty=Decimal("0"),
):
    return CDSLCASTransaction(
        isin=isin,
        security_name=security_name,
        transaction_particulars=transaction_particulars,
        transaction_date=transaction_date,
        opening_balance=opening_balance,
        credit=credit,
        debit=debit,
        closing_balance=closing_balance,
        stamp_duty=stamp_duty,
    )


def test_imports_new_transaction(
    db_session,
):
    user = create_user(
        db_session,
        "service_user_one@example.com",
    )

    service = PortfolioTransactionService(
        db_session,
    )

    transaction = create_cas_transaction()

    result = service.import_transaction(
        user_id=user.id,
        transaction=transaction,
    )

    assert result is not None
    assert result.user_id == user.id
    assert result.isin == "INF843K01AO4"
    assert result.quantity == Decimal("0.790")
    assert result.source == "CDSL"


def test_duplicate_transaction_is_not_imported(
    db_session,
):
    user = create_user(
        db_session,
        "service_user_two@example.com",
    )

    service = PortfolioTransactionService(
        db_session,
    )

    transaction = create_cas_transaction()

    first = service.import_transaction(
        user_id=user.id,
        transaction=transaction,
    )

    second = service.import_transaction(
        user_id=user.id,
        transaction=transaction,
    )

    assert first.id == second.id


def test_same_transaction_can_exist_for_different_users(
    db_session,
):
    user_one = create_user(
        db_session,
        "service_user_three@example.com",
        "User One",
    )

    user_two = create_user(
        db_session,
        "service_user_four@example.com",
        "User Two",
    )

    service = PortfolioTransactionService(
        db_session,
    )

    transaction = create_cas_transaction()

    user_one_transaction = service.import_transaction(
        user_id=user_one.id,
        transaction=transaction,
    )

    user_two_transaction = service.import_transaction(
        user_id=user_two.id,
        transaction=transaction,
    )

    assert user_one_transaction.id != user_two_transaction.id
    assert user_one_transaction.user_id == user_one.id
    assert user_two_transaction.user_id == user_two.id


def test_imports_multiple_transactions(
    db_session,
):
    user = create_user(
        db_session,
        "service_user_five@example.com",
    )

    service = PortfolioTransactionService(
        db_session,
    )

    transaction_one = create_cas_transaction(
        isin="INF843K01AO4",
        transaction_date=date(2026, 7, 1),
    )

    transaction_two = create_cas_transaction(
        isin="INF205K013T3",
        security_name="INVESCO ASSET MANAGEMENT",
        transaction_date=date(2026, 7, 2),
        credit=Decimal("1.841"),
        closing_balance=Decimal("1.841"),
    )

    result_one = service.import_transaction(
        user_id=user.id,
        transaction=transaction_one,
    )

    result_two = service.import_transaction(
        user_id=user.id,
        transaction=transaction_two,
    )

    assert result_one.id != result_two.id
    assert result_one.isin == "INF843K01AO4"
    assert result_two.isin == "INF205K013T3"
