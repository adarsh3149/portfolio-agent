from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.cdsl_transaction_event import (
    CDSLTransactionEvent,
)
from app.models.user import User
from app.repositories.cdsl_transaction_event_repository import (
    CDSLTransactionEventRepository,
)
from app.schemas.cdsl import CDSLTransactionDirection


def create_user(
    db_session,
    email: str,
):
    user = User(
        name="CDSL Test User",
        email=email,
        password_hash="password",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def create_event(
    user_id: int,
    source_reference: str,
    isin: str = "INF843K01AO4",
    quantity: Decimal = Decimal("0.771"),
    direction: CDSLTransactionDirection = (
        CDSLTransactionDirection.CREDIT
    ),
):
    return CDSLTransactionEvent(
        user_id=user_id,
        security_name="Edelweiss Mid Cap Fund",
        isin=isin,
        quantity=quantity,
        direction=direction,
        transaction_datetime=datetime(
            2026,
            8,
            10,
            23,
            17,
            3,
        ),
        source="CDSL",
        source_reference=source_reference,
    )


def test_create_event(
    db_session,
):
    repository = CDSLTransactionEventRepository(
        db_session,
    )

    user = create_user(
        db_session,
        "cdsl_create@example.com",
    )

    event = create_event(
        user_id=user.id,
        source_reference="event-001",
    )

    result = repository.create(event)

    assert result.id is not None
    assert result.user_id == user.id
    assert result.isin == "INF843K01AO4"
    assert result.quantity == Decimal("0.771")
    assert result.direction == (
        CDSLTransactionDirection.CREDIT
    )
    assert result.source == "CDSL"
    assert result.source_reference == "event-001"
    assert result.processed is False


def test_get_by_source_reference(
    db_session,
):
    repository = CDSLTransactionEventRepository(
        db_session,
    )

    user = create_user(
        db_session,
        "cdsl_lookup@example.com",
    )

    event = create_event(
        user_id=user.id,
        source_reference="event-002",
    )

    repository.create(event)

    result = repository.get_by_source_reference(
        user_id=user.id,
        source="CDSL",
        source_reference="event-002",
    )

    assert result is not None
    assert result.id == event.id
    assert result.source_reference == "event-002"


def test_get_by_source_reference_returns_none_for_missing_event(
    db_session,
):
    repository = CDSLTransactionEventRepository(
        db_session,
    )

    user = create_user(
        db_session,
        "cdsl_missing@example.com",
    )

    result = repository.get_by_source_reference(
        user_id=user.id,
        source="CDSL",
        source_reference="does-not-exist",
    )

    assert result is None


def test_get_by_source_reference_is_user_isolated(
    db_session,
):
    repository = CDSLTransactionEventRepository(
        db_session,
    )

    user_1 = create_user(
        db_session,
        "cdsl_user1@example.com",
    )

    user_2 = create_user(
        db_session,
        "cdsl_user2@example.com",
    )

    event = create_event(
        user_id=user_1.id,
        source_reference="event-003",
    )

    repository.create(event)

    result = repository.get_by_source_reference(
        user_id=user_2.id,
        source="CDSL",
        source_reference="event-003",
    )

    assert result is None


def test_get_by_user(
    db_session,
):
    repository = CDSLTransactionEventRepository(
        db_session,
    )

    user_1 = create_user(
        db_session,
        "cdsl_list_user1@example.com",
    )

    user_2 = create_user(
        db_session,
        "cdsl_list_user2@example.com",
    )

    event_1 = create_event(
        user_id=user_1.id,
        source_reference="event-004",
        isin="INF843K01AO4",
    )

    event_2 = create_event(
        user_id=user_1.id,
        source_reference="event-005",
        isin="INF205K013T3",
        quantity=Decimal("1.847"),
    )

    event_3 = create_event(
        user_id=user_2.id,
        source_reference="event-006",
    )

    repository.create(event_1)
    repository.create(event_2)
    repository.create(event_3)

    result = repository.get_by_user(
        user_id=user_1.id,
    )

    assert len(result) == 2

    assert {
        event.source_reference
        for event in result
    } == {
        "event-004",
        "event-005",
    }


def test_duplicate_source_reference_is_rejected(
    db_session,
):
    repository = CDSLTransactionEventRepository(
        db_session,
    )

    user = create_user(
        db_session,
        "cdsl_duplicate@example.com",
    )

    event_1 = create_event(
        user_id=user.id,
        source_reference="event-007",
    )

    repository.create(event_1)

    event_2 = create_event(
        user_id=user.id,
        source_reference="event-007",
    )

    with pytest.raises(IntegrityError):
        repository.create(event_2)

    db_session.rollback()