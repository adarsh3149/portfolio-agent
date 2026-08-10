from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.portfolio_snapshot import PortfolioSnapshot
from app.models.user import User
from app.repositories.portfolio_snapshot_repository import (
    PortfolioSnapshotRepository,
)


def create_user(
    db_session,
    email: str,
):
    user = User(
        name="Snapshot User",
        email=email,
        password_hash="test-password",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def create_snapshot(
    db_session,
    user_id: int,
    snapshot_date: date,
    invested: Decimal = Decimal("10000.00"),
    market_value: Decimal = Decimal("12000.00"),
    realized: Decimal = Decimal("500.00"),
    unrealized: Decimal = Decimal("1500.00"),
    total_profit_loss: Decimal = Decimal("2000.00"),
):
    snapshot = PortfolioSnapshot(
        user_id=user_id,
        snapshot_date=snapshot_date,
        total_invested=invested,
        total_market_value=market_value,
        total_realized_profit_loss=realized,
        total_unrealized_profit_loss=unrealized,
        total_profit_loss=total_profit_loss,
    )

    db_session.add(snapshot)
    db_session.commit()
    db_session.refresh(snapshot)

    return snapshot


def test_create_snapshot(db_session):
    user = create_user(
        db_session,
        "snapshot_create@example.com",
    )

    repository = PortfolioSnapshotRepository(
        db_session
    )

    snapshot = repository.create(
        PortfolioSnapshot(
            user_id=user.id,
            snapshot_date=date(2026, 8, 10),
            total_invested=Decimal("10000.00"),
            total_market_value=Decimal("12000.00"),
            total_realized_profit_loss=Decimal("500.00"),
            total_unrealized_profit_loss=Decimal("1500.00"),
            total_profit_loss=Decimal("2000.00"),
        )
    )

    assert snapshot.id is not None
    assert snapshot.user_id == user.id
    assert snapshot.snapshot_date == date(2026, 8, 10)

    assert snapshot.total_invested == Decimal("10000.00")
    assert snapshot.total_market_value == Decimal("12000.00")
    assert snapshot.total_realized_profit_loss == Decimal("500.00")
    assert snapshot.total_unrealized_profit_loss == Decimal("1500.00")
    assert snapshot.total_profit_loss == Decimal("2000.00")


def test_get_snapshot_by_user_and_date(
    db_session,
):
    user = create_user(
        db_session,
        "snapshot_get@example.com",
    )

    create_snapshot(
        db_session=db_session,
        user_id=user.id,
        snapshot_date=date(2026, 8, 10),
    )

    repository = PortfolioSnapshotRepository(
        db_session
    )

    snapshot = repository.get_by_user_and_date(
        user_id=user.id,
        snapshot_date=date(2026, 8, 10),
    )

    assert snapshot is not None
    assert snapshot.user_id == user.id
    assert snapshot.snapshot_date == date(2026, 8, 10)


def test_get_snapshots_by_user_ordered_by_date(
    db_session,
):
    user = create_user(
        db_session,
        "snapshot_history@example.com",
    )

    create_snapshot(
        db_session=db_session,
        user_id=user.id,
        snapshot_date=date(2026, 8, 12),
    )

    create_snapshot(
        db_session=db_session,
        user_id=user.id,
        snapshot_date=date(2026, 8, 10),
    )

    create_snapshot(
        db_session=db_session,
        user_id=user.id,
        snapshot_date=date(2026, 8, 11),
    )

    repository = PortfolioSnapshotRepository(
        db_session
    )

    snapshots = repository.get_by_user(
        user_id=user.id,
    )

    assert len(snapshots) == 3

    assert [
        snapshot.snapshot_date
        for snapshot in snapshots
    ] == [
        date(2026, 8, 10),
        date(2026, 8, 11),
        date(2026, 8, 12),
    ]


def test_snapshot_repository_is_user_isolated(
    db_session,
):
    user_1 = create_user(
        db_session,
        "snapshot_user1@example.com",
    )

    user_2 = create_user(
        db_session,
        "snapshot_user2@example.com",
    )

    create_snapshot(
        db_session=db_session,
        user_id=user_1.id,
        snapshot_date=date(2026, 8, 10),
    )

    repository = PortfolioSnapshotRepository(
        db_session
    )

    user_1_snapshots = repository.get_by_user(
        user_id=user_1.id,
    )

    user_2_snapshots = repository.get_by_user(
        user_id=user_2.id,
    )

    assert len(user_1_snapshots) == 1
    assert user_1_snapshots[0].user_id == user_1.id

    assert user_2_snapshots == []


def test_duplicate_snapshot_for_same_user_and_date_is_rejected(
    db_session,
):
    user = create_user(
        db_session,
        "snapshot_duplicate@example.com",
    )

    create_snapshot(
        db_session=db_session,
        user_id=user.id,
        snapshot_date=date(2026, 8, 10),
    )

    duplicate = PortfolioSnapshot(
        user_id=user.id,
        snapshot_date=date(2026, 8, 10),
        total_invested=Decimal("11000.00"),
        total_market_value=Decimal("13000.00"),
        total_realized_profit_loss=Decimal("600.00"),
        total_unrealized_profit_loss=Decimal("1400.00"),
        total_profit_loss=Decimal("2000.00"),
    )

    db_session.add(duplicate)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()

def test_get_snapshots_by_user_with_start_date(
    db_session,
):
    user = create_user(
        db_session,
        "snapshot_start_date@example.com",
    )

    create_snapshot(
        db_session,
        user.id,
        date(2026, 8, 8),
    )

    create_snapshot(
        db_session,
        user.id,
        date(2026, 8, 9),
    )

    create_snapshot(
        db_session,
        user.id,
        date(2026, 8, 10),
    )

    repository = PortfolioSnapshotRepository(
        db_session
    )

    snapshots = repository.get_by_user(
        user_id=user.id,
        start_date=date(2026, 8, 9),
    )

    assert [
        snapshot.snapshot_date
        for snapshot in snapshots
    ] == [
        date(2026, 8, 9),
        date(2026, 8, 10),
    ]


def test_get_snapshots_by_user_with_end_date(
    db_session,
):
    user = create_user(
        db_session,
        "snapshot_end_date@example.com",
    )

    create_snapshot(
        db_session,
        user.id,
        date(2026, 8, 8),
    )

    create_snapshot(
        db_session,
        user.id,
        date(2026, 8, 9),
    )

    create_snapshot(
        db_session,
        user.id,
        date(2026, 8, 10),
    )

    repository = PortfolioSnapshotRepository(
        db_session
    )

    snapshots = repository.get_by_user(
        user_id=user.id,
        end_date=date(2026, 8, 9),
    )

    assert [
        snapshot.snapshot_date
        for snapshot in snapshots
    ] == [
        date(2026, 8, 8),
        date(2026, 8, 9),
    ]


def test_get_snapshots_by_user_with_date_range(
    db_session,
):
    user = create_user(
        db_session,
        "snapshot_date_range@example.com",
    )

    create_snapshot(
        db_session,
        user.id,
        date(2026, 8, 7),
    )

    create_snapshot(
        db_session,
        user.id,
        date(2026, 8, 8),
    )

    create_snapshot(
        db_session,
        user.id,
        date(2026, 8, 9),
    )

    create_snapshot(
        db_session,
        user.id,
        date(2026, 8, 10),
    )

    repository = PortfolioSnapshotRepository(
        db_session
    )

    snapshots = repository.get_by_user(
        user_id=user.id,
        start_date=date(2026, 8, 8),
        end_date=date(2026, 8, 9),
    )

    assert [
        snapshot.snapshot_date
        for snapshot in snapshots
    ] == [
        date(2026, 8, 8),
        date(2026, 8, 9),
    ]
