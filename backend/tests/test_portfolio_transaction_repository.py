from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.portfolio_transaction import PortfolioTransaction
from app.repositories.portfolio_transaction_repository import (
    PortfolioTransactionRepository,
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


def create_transaction(
    db_session,
    user_id,
    source_reference,
    isin="INF843K01AO4",
):
    transaction = PortfolioTransaction(
        user_id=user_id,
        isin=isin,
        security_name="EDELWEISS MID CAP FUND",
        transaction_date=date(2026, 7, 1),
        transaction_type="BUY",
        quantity=Decimal("0.790"),
        source="CDSL",
        source_reference=source_reference,
    )

    db_session.add(transaction)
    db_session.commit()

    return transaction


def test_create_transaction(
    db_session,
):
    user = create_user(
        db_session,
        "portfolio_one@example.com",
    )

    repository = PortfolioTransactionRepository(
        db_session,
    )

    transaction = repository.create(
        user_id=user.id,
        isin="INF843K01AO4",
        security_name="EDELWEISS MID CAP FUND",
        transaction_date=date(2026, 7, 1),
        transaction_type="BUY",
        quantity=Decimal("0.790"),
        source="CDSL",
        source_reference="cdsl-reference-001",
    )

    assert transaction.id is not None
    assert transaction.user_id == user.id
    assert transaction.isin == "INF843K01AO4"
    assert transaction.quantity == Decimal("0.790")


def test_get_by_source_reference(
    db_session,
):
    user = create_user(
        db_session,
        "portfolio_two@example.com",
    )

    transaction = create_transaction(
        db_session,
        user.id,
        "cdsl-reference-002",
    )

    repository = PortfolioTransactionRepository(
        db_session,
    )

    result = repository.get_by_source_reference(
        user_id=user.id,
        source_reference="cdsl-reference-002",
    )

    assert result is not None
    assert result.id == transaction.id


def test_get_by_source_reference_returns_none_for_missing_transaction(
    db_session,
):
    user = create_user(
        db_session,
        "portfolio_three@example.com",
    )

    repository = PortfolioTransactionRepository(
        db_session,
    )

    result = repository.get_by_source_reference(
        user_id=user.id,
        source_reference="does-not-exist",
    )

    assert result is None


def test_get_by_source_reference_is_user_isolated(
    db_session,
):
    user_one = create_user(
        db_session,
        "portfolio_four@example.com",
        "User One",
    )

    user_two = create_user(
        db_session,
        "portfolio_five@example.com",
        "User Two",
    )

    create_transaction(
        db_session,
        user_one.id,
        "shared-reference",
    )

    repository = PortfolioTransactionRepository(
        db_session,
    )

    result = repository.get_by_source_reference(
        user_id=user_two.id,
        source_reference="shared-reference",
    )

    assert result is None


def test_get_by_user(
    db_session,
):
    user = create_user(
        db_session,
        "portfolio_six@example.com",
    )

    create_transaction(
        db_session,
        user.id,
        "reference-001",
    )

    create_transaction(
        db_session,
        user.id,
        "reference-002",
        isin="INF205K013T3",
    )

    repository = PortfolioTransactionRepository(
        db_session,
    )

    transactions = repository.get_by_user(
        user.id,
    )

    assert len(transactions) == 2

    assert {
        transaction.source_reference
        for transaction in transactions
    } == {
        "reference-001",
        "reference-002",
    }


def test_duplicate_source_reference_is_rejected(
    db_session,
):
    user = create_user(
        db_session,
        "portfolio_seven@example.com",
    )

    create_transaction(
        db_session,
        user.id,
        "duplicate-reference",
    )

    repository = PortfolioTransactionRepository(
        db_session,
    )

    with pytest.raises(
        IntegrityError,
    ):
        repository.create(
            user_id=user.id,
            isin="INF843K01AO4",
            security_name="EDELWEISS MID CAP FUND",
            transaction_date=date(2026, 7, 1),
            transaction_type="BUY",
            quantity=Decimal("0.500"),
            source="CDSL",
            source_reference="duplicate-reference",
        )

        db_session.commit()
