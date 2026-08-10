from datetime import date
from decimal import Decimal

from app.models.portfolio_snapshot import PortfolioSnapshot
from app.models.user import User
from app.repositories.portfolio_snapshot_repository import (
    PortfolioSnapshotRepository,
)
from app.services.portfolio_snapshot_service import (
    PortfolioSnapshotService,
)


def create_user(
    db_session,
    email: str,
):
    user = User(
        name="Snapshot Service User",
        email=email,
        password_hash="test-password",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


class FakePortfolioPerformanceService:

    def __init__(
        self,
        total_invested: Decimal,
        total_market_value: Decimal,
        total_realized_profit_loss: Decimal,
        total_unrealized_profit_loss: Decimal,
        total_profit_loss: Decimal,
    ):
        self.result = type(
            "PerformanceResult",
            (),
            {
                "total_invested": total_invested,
                "total_market_value": total_market_value,
                "total_realized_profit_loss":
                    total_realized_profit_loss,
                "total_unrealized_profit_loss":
                    total_unrealized_profit_loss,
                "total_profit_loss": total_profit_loss,
            },
        )()

    def get_performance(
        self,
        user_id: int,
    ):
        return self.result


def create_service(
    db_session,
    performance_service,
):
    repository = PortfolioSnapshotRepository(
        db_session
    )

    return PortfolioSnapshotService(
        performance_service=performance_service,
        repository=repository,
    )


def test_create_daily_snapshot(
    db_session,
):
    user = create_user(
        db_session,
        "snapshot_service_create@example.com",
    )

    performance_service = FakePortfolioPerformanceService(
        total_invested=Decimal("10000.00"),
        total_market_value=Decimal("12000.00"),
        total_realized_profit_loss=Decimal("500.00"),
        total_unrealized_profit_loss=Decimal("1500.00"),
        total_profit_loss=Decimal("2000.00"),
    )

    service = create_service(
        db_session,
        performance_service,
    )

    snapshot = service.create_snapshot(
        user_id=user.id,
        snapshot_date=date(2026, 8, 10),
    )

    assert snapshot.id is not None
    assert snapshot.user_id == user.id
    assert snapshot.snapshot_date == date(2026, 8, 10)

    assert snapshot.total_invested == Decimal("10000.00")
    assert snapshot.total_market_value == Decimal("12000.00")
    assert (
        snapshot.total_realized_profit_loss
        == Decimal("500.00")
    )
    assert (
        snapshot.total_unrealized_profit_loss
        == Decimal("1500.00")
    )
    assert snapshot.total_profit_loss == Decimal("2000.00")


def test_snapshot_uses_current_portfolio_performance(
    db_session,
):
    user = create_user(
        db_session,
        "snapshot_service_performance@example.com",
    )

    performance_service = FakePortfolioPerformanceService(
        total_invested=Decimal("25000.00"),
        total_market_value=Decimal("27500.00"),
        total_realized_profit_loss=Decimal("1000.00"),
        total_unrealized_profit_loss=Decimal("1500.00"),
        total_profit_loss=Decimal("2500.00"),
    )

    service = create_service(
        db_session,
        performance_service,
    )

    snapshot = service.create_snapshot(
        user_id=user.id,
        snapshot_date=date(2026, 8, 10),
    )

    assert snapshot.total_invested == Decimal("25000.00")
    assert snapshot.total_market_value == Decimal("27500.00")
    assert (
        snapshot.total_realized_profit_loss
        == Decimal("1000.00")
    )
    assert (
        snapshot.total_unrealized_profit_loss
        == Decimal("1500.00")
    )
    assert snapshot.total_profit_loss == Decimal("2500.00")


def test_create_snapshot_is_user_specific(
    db_session,
):
    user_1 = create_user(
        db_session,
        "snapshot_service_user1@example.com",
    )

    user_2 = create_user(
        db_session,
        "snapshot_service_user2@example.com",
    )

    performance_service = FakePortfolioPerformanceService(
        total_invested=Decimal("10000.00"),
        total_market_value=Decimal("12000.00"),
        total_realized_profit_loss=Decimal("500.00"),
        total_unrealized_profit_loss=Decimal("1500.00"),
        total_profit_loss=Decimal("2000.00"),
    )

    service = create_service(
        db_session,
        performance_service,
    )

    snapshot_1 = service.create_snapshot(
        user_id=user_1.id,
        snapshot_date=date(2026, 8, 10),
    )

    snapshot_2 = service.create_snapshot(
        user_id=user_2.id,
        snapshot_date=date(2026, 8, 10),
    )

    assert snapshot_1.user_id == user_1.id
    assert snapshot_2.user_id == user_2.id

    assert snapshot_1.id != snapshot_2.id


def test_existing_snapshot_is_updated(
    db_session,
):
    user = create_user(
        db_session,
        "snapshot_service_update@example.com",
    )

    initial_performance = FakePortfolioPerformanceService(
        total_invested=Decimal("10000.00"),
        total_market_value=Decimal("12000.00"),
        total_realized_profit_loss=Decimal("500.00"),
        total_unrealized_profit_loss=Decimal("1500.00"),
        total_profit_loss=Decimal("2000.00"),
    )

    service = create_service(
        db_session,
        initial_performance,
    )

    snapshot = service.create_snapshot(
        user_id=user.id,
        snapshot_date=date(2026, 8, 10),
    )

    snapshot_id = snapshot.id

    updated_performance = FakePortfolioPerformanceService(
        total_invested=Decimal("10000.00"),
        total_market_value=Decimal("13000.00"),
        total_realized_profit_loss=Decimal("700.00"),
        total_unrealized_profit_loss=Decimal("2300.00"),
        total_profit_loss=Decimal("3000.00"),
    )

    updated_service = create_service(
        db_session,
        updated_performance,
    )

    updated_snapshot = updated_service.create_snapshot(
        user_id=user.id,
        snapshot_date=date(2026, 8, 10),
    )

    assert updated_snapshot.id == snapshot_id

    assert updated_snapshot.total_invested == Decimal(
        "10000.00"
    )

    assert updated_snapshot.total_market_value == Decimal(
        "13000.00"
    )

    assert (
        updated_snapshot.total_realized_profit_loss
        == Decimal("700.00")
    )

    assert (
        updated_snapshot.total_unrealized_profit_loss
        == Decimal("2300.00")
    )

    assert updated_snapshot.total_profit_loss == Decimal(
        "3000.00"
    )
