from datetime import date
from decimal import Decimal

from app.jobs.run_daily_snapshot import run_daily_snapshot
from app.models.asset import Asset
from app.models.market_price import MarketPrice
from app.models.transaction import Transaction
from app.models.user import User
from app.enums import TransactionType
from app.models.portfolio_snapshot import PortfolioSnapshot


def test_run_daily_snapshot_creates_snapshot(
    db_session,
):
    user = User(
        name="Daily Snapshot User",
        email="daily_snapshot@example.com",
        password_hash="test-password",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    asset = Asset(
        symbol="INFY",
        name="Infosys",
        asset_type="STOCK",
        exchange="NSE",
        currency="INR",
    )

    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)

    transaction = Transaction(
        user_id=user.id,
        asset_id=asset.id,
        transaction_type=TransactionType.BUY,
        quantity=Decimal("100"),
        price=Decimal("50"),
        amount=Decimal("5000"),
        charges=Decimal("20"),
        transaction_date=date(2026, 8, 10),
    )

    db_session.add(transaction)

    market_price = MarketPrice(
        asset_id=asset.id,
        price=Decimal("60"),
        source="test",
        price_time="2026-08-10T10:30:00+00:00",
    )

    db_session.add(market_price)
    db_session.commit()

    snapshots = run_daily_snapshot(
        snapshot_date=date(2026, 8, 10),
        db=db_session,
    )

    snapshot = (
        db_session.query(PortfolioSnapshot)
        .filter(
            PortfolioSnapshot.user_id == user.id,
            PortfolioSnapshot.snapshot_date
            == date(2026, 8, 10)
        )
        .one()
    )

    user_snapshots = [
        snapshot
        for snapshot in snapshots
        if snapshot.user_id == user.id
    ]

    assert len(user_snapshots) == 1

    snapshot = user_snapshots[0]

    assert snapshot.user_id == user.id
    assert snapshot.snapshot_date == date(2026, 8, 10)

    assert snapshot.total_invested == Decimal("5020.00")
    assert snapshot.total_market_value == Decimal(
        "6000.000000000000"
    )

    assert (
        snapshot.total_realized_profit_loss
        == Decimal("0")
    )

    assert (
        snapshot.total_unrealized_profit_loss
        == Decimal("980.000000000000")
    )

    assert (
        snapshot.total_profit_loss
        == Decimal("980.000000000000")
    )

def test_run_daily_snapshot_processes_all_users(
    db_session,
):
    user_1 = User(
        name="Snapshot User One",
        email="snapshot_user_one@example.com",
        password_hash="test-password",
    )

    user_2 = User(
        name="Snapshot User Two",
        email="snapshot_user_two@example.com",
        password_hash="test-password",
    )

    db_session.add_all([
        user_1,
        user_2,
    ])
    db_session.commit()

    asset = Asset(
        symbol="INFY",
        name="Infosys",
        asset_type="STOCK",
        exchange="NSE",
        currency="INR",
    )

    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)

    transaction = Transaction(
        user_id=user_1.id,
        asset_id=asset.id,
        transaction_type=TransactionType.BUY,
        quantity=Decimal("100"),
        price=Decimal("50"),
        amount=Decimal("5000"),
        charges=Decimal("20"),
        transaction_date=date(2026, 8, 10),
    )

    db_session.add(transaction)

    market_price = MarketPrice(
        asset_id=asset.id,
        price=Decimal("60"),
        source="test",
        price_time="2026-08-10T10:30:00+00:00",
    )

    db_session.add(market_price)
    db_session.commit()

    run_daily_snapshot(
        snapshot_date=date(2026, 8, 10),
        db=db_session,
    )

    snapshots = (
        db_session.query(PortfolioSnapshot)
        .filter(
            PortfolioSnapshot.snapshot_date
            == date(2026, 8, 10),
        )
        .all()
    )

    user_ids = {
        snapshot.user_id
        for snapshot in snapshots
    }

    assert user_1.id in user_ids
    assert user_2.id in user_ids

def test_run_daily_snapshot_creates_zero_snapshot_for_user_without_portfolio(
    db_session,
):
    user = User(
        name="Empty Portfolio User",
        email="empty_daily_snapshot@example.com",
        password_hash="test-password",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    run_daily_snapshot(
        snapshot_date=date(2026, 8, 10),
        db=db_session,
    )

    snapshot = (
        db_session.query(PortfolioSnapshot)
        .filter(
            PortfolioSnapshot.user_id == user.id,
            PortfolioSnapshot.snapshot_date
            == date(2026, 8, 10),
        )
        .one()
    )

    assert snapshot.total_invested == Decimal("0")
    assert snapshot.total_market_value == Decimal("0")
    assert snapshot.total_realized_profit_loss == Decimal("0")
    assert snapshot.total_unrealized_profit_loss == Decimal("0")
    assert snapshot.total_profit_loss == Decimal("0")

def test_run_daily_snapshot_updates_existing_snapshot(
    db_session,
):
    user = User(
        name="Repeat Snapshot User",
        email="repeat_daily_snapshot@example.com",
        password_hash="test-password",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    asset = Asset(
        symbol="INFY",
        name="Infosys",
        asset_type="STOCK",
        exchange="NSE",
        currency="INR",
    )

    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)

    transaction = Transaction(
        user_id=user.id,
        asset_id=asset.id,
        transaction_type=TransactionType.BUY,
        quantity=Decimal("100"),
        price=Decimal("50"),
        amount=Decimal("5000"),
        charges=Decimal("20"),
        transaction_date=date(2026, 8, 10),
    )

    db_session.add(transaction)

    market_price = MarketPrice(
        asset_id=asset.id,
        price=Decimal("60"),
        source="test",
        price_time="2026-08-10T10:30:00+00:00",
    )

    db_session.add(market_price)
    db_session.commit()

    run_daily_snapshot(
        snapshot_date=date(2026, 8, 10),
        db=db_session,
    )

    first_snapshot = (
        db_session.query(PortfolioSnapshot)
        .filter(
            PortfolioSnapshot.user_id == user.id,
            PortfolioSnapshot.snapshot_date
            == date(2026, 8, 10),
        )
        .one()
    )

    first_snapshot_id = first_snapshot.id

    run_daily_snapshot(
        snapshot_date=date(2026, 8, 10),
        db=db_session,
    )

    snapshots = (
        db_session.query(PortfolioSnapshot)
        .filter(
            PortfolioSnapshot.user_id == user.id,
            PortfolioSnapshot.snapshot_date
            == date(2026, 8, 10),
        )
        .all()
    )

    assert len(snapshots) == 1
    assert snapshots[0].id == first_snapshot_id