from datetime import UTC, datetime
from decimal import Decimal

from app.enums import AssetType, Currency, Exchange, TransactionType
from app.models.asset import Asset
from app.models.cdsl_transaction_event import CDSLTransactionEvent
from app.models.market_price import MarketPrice
from app.models.user import User
from app.repositories.asset_repository import AssetRepository
from app.repositories.cdsl_transaction_event_repository import (
    CDSLTransactionEventRepository,
)
from app.repositories.market_price_repository import MarketPriceRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.cdsl import CDSLTransactionDirection
from app.services.cdsl.transaction_processor import (
    CDSLTransactionProcessor,
)


def create_user(db_session) -> User:
    user = User(
        name="CDSL Processor User",
        email="cdsl_processor@example.com",
        password_hash="password",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_event(
    db_session,
    user_id: int,
    isin: str = "INF123456789",
    processed: bool = False,
) -> CDSLTransactionEvent:
    event = CDSLTransactionEvent(
        user_id=user_id,
        security_name="HDFC Small Cap Fund",
        isin=isin,
        quantity=Decimal("10.5"),
        direction=CDSLTransactionDirection.CREDIT,
        transaction_datetime=datetime(2026, 8, 22, 10, 30, tzinfo=UTC),
        source="CDSL",
        source_reference=f"event-{isin}-{processed}",
        processed=processed,
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


def create_asset(db_session, isin: str = "INF123456789") -> Asset:
    asset = Asset(
        symbol="HDFCSMALL",
        name="HDFC Small Cap Fund",
        asset_type=AssetType.MUTUAL_FUND,
        exchange=Exchange.AMFI,
        currency=Currency.INR,
        isin=isin,
    )
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    return asset


def create_processor(db_session) -> CDSLTransactionProcessor:
    return CDSLTransactionProcessor(
        event_repository=CDSLTransactionEventRepository(db_session),
        asset_repository=AssetRepository(db_session),
        market_price_repository=MarketPriceRepository(db_session),
        transaction_repository=TransactionRepository(db_session),
    )


def test_process_unprocessed_credit_event_creates_buy_transaction(
    db_session,
):
    user = create_user(db_session)
    event = create_event(db_session, user.id)
    asset = create_asset(db_session)
    db_session.add(
        MarketPrice(
            asset_id=asset.id,
            price=Decimal("100.0000"),
            source="TEST",
            price_time=datetime(2026, 8, 22, 10, 0, tzinfo=UTC),
        )
    )
    db_session.commit()

    transactions = create_processor(db_session).process_unprocessed_events(
        user.id,
    )

    assert len(transactions) == 1
    transaction = transactions[0]
    assert transaction.user_id == user.id
    assert transaction.asset_id == asset.id
    assert transaction.transaction_type == TransactionType.BUY
    assert transaction.quantity == Decimal("10.5")
    assert transaction.price == Decimal("100.0000")
    assert transaction.amount == Decimal("1050.0000")
    assert transaction.transaction_date == event.transaction_datetime.date()
    assert event.processed is True


def test_process_event_leaves_event_pending_when_asset_is_missing(
    db_session,
):
    user = create_user(db_session)
    event = create_event(db_session, user.id)

    result = create_processor(db_session).process_event(event)

    assert result is None
    assert event.processed is False


def test_process_event_leaves_event_pending_when_market_price_is_missing(
    db_session,
):
    user = create_user(db_session)
    event = create_event(db_session, user.id)
    create_asset(db_session)

    result = create_processor(db_session).process_event(event)

    assert result is None
    assert event.processed is False


def test_process_event_skips_already_processed_event(
    db_session,
):
    user = create_user(db_session)
    event = create_event(db_session, user.id, processed=True)
    create_asset(db_session)

    result = create_processor(db_session).process_event(event)

    assert result is None
    assert event.processed is True
