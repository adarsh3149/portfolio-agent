from datetime import date, datetime, UTC
from decimal import Decimal

from app.enums import TransactionType
from app.models.asset import Asset
from app.models.market_price import MarketPrice
from app.models.transaction import Transaction
from app.models.user import User
from app.repositories.market_price_repository import (
    MarketPriceRepository,
)
from app.repositories.transaction_repository import (
    TransactionRepository,
)
from app.services.holding_service import HoldingService
from app.services.performance_service import PerformanceService
from app.services.portfolio_performance_service import (
    PortfolioPerformanceService,
)


def create_user(
    db_session,
    email: str,
):
    user = User(
        name="Portfolio Performance User",
        email=email,
        password_hash="test-password",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def create_asset(
    db_session,
    symbol: str = "INFY",
    name: str = "Infosys",
):
    asset = Asset(
        symbol=symbol,
        name=name,
        asset_type="STOCK",
        exchange="NSE",
        currency="INR",
    )

    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)

    return asset


def create_transaction(
    db_session,
    user_id: int,
    asset_id: int,
    transaction_type: TransactionType,
    quantity: Decimal,
    price: Decimal,
    amount: Decimal,
    charges: Decimal,
):
    transaction = Transaction(
        user_id=user_id,
        asset_id=asset_id,
        transaction_type=transaction_type,
        quantity=quantity,
        price=price,
        amount=amount,
        charges=charges,
        transaction_date=date(2026, 8, 9),
    )

    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)

    return transaction


def create_market_price(
    db_session,
    asset_id: int,
    price: Decimal,
):
    market_price = MarketPrice(
        asset_id=asset_id,
        price=price,
        source="test",
        price_time=datetime(
            2026,
            8,
            9,
            10,
            30,
            tzinfo=UTC,
        ),
    )

    db_session.add(market_price)
    db_session.commit()
    db_session.refresh(market_price)

    return market_price


def create_service(
    db_session,
):
    transaction_repository = TransactionRepository(
        db_session
    )

    market_price_repository = MarketPriceRepository(
        db_session
    )

    holding_service = HoldingService(
        transaction_repository
    )

    performance_service = PerformanceService(
        transaction_repository
    )

    return PortfolioPerformanceService(
        holding_service=holding_service,
        performance_service=performance_service,
        market_price_repository=market_price_repository,
    )


def test_buy_only_portfolio_performance(
    db_session,
):
    user = create_user(
        db_session,
        "portfolio_performance_buy@example.com",
    )

    asset = create_asset(db_session)

    create_transaction(
        db_session=db_session,
        user_id=user.id,
        asset_id=asset.id,
        transaction_type=TransactionType.BUY,
        quantity=Decimal("100"),
        price=Decimal("50"),
        amount=Decimal("5000"),
        charges=Decimal("20"),
    )

    create_market_price(
        db_session,
        asset.id,
        Decimal("60"),
    )

    service = create_service(db_session)

    result = service.get_performance(
        user_id=user.id,
    )

    assert result.total_invested == Decimal("5020")
    assert result.total_market_value == Decimal("6000")

    assert (
        result.total_realized_profit_loss
        == Decimal("0")
    )

    assert (
        result.total_unrealized_profit_loss
        == Decimal("980")
    )

    assert result.total_profit_loss == Decimal("980")


def test_buy_then_sell_portfolio_performance(
    db_session,
):
    user = create_user(
        db_session,
        "portfolio_performance_sell@example.com",
    )

    asset = create_asset(db_session)

    create_transaction(
        db_session=db_session,
        user_id=user.id,
        asset_id=asset.id,
        transaction_type=TransactionType.BUY,
        quantity=Decimal("100"),
        price=Decimal("50"),
        amount=Decimal("5000"),
        charges=Decimal("20"),
    )

    create_transaction(
        db_session=db_session,
        user_id=user.id,
        asset_id=asset.id,
        transaction_type=TransactionType.SELL,
        quantity=Decimal("50"),
        price=Decimal("70"),
        amount=Decimal("3500"),
        charges=Decimal("10"),
    )

    create_market_price(
        db_session,
        asset.id,
        Decimal("60"),
    )

    service = create_service(db_session)

    result = service.get_performance(
        user_id=user.id,
    )

    # Realized:
    # 3500 - 2510 - 10 = 980
    assert (
        result.total_realized_profit_loss
        == Decimal("980")
    )

    # Remaining:
    # 50 units × 50.20 = 2510
    assert result.total_invested == Decimal("2510")

    # Market value:
    # 50 × 60 = 3000
    assert result.total_market_value == Decimal("3000")

    # Unrealized:
    # 3000 - 2510 = 490
    assert (
        result.total_unrealized_profit_loss
        == Decimal("490")
    )

    # Total:
    # 980 + 490 = 1470
    assert result.total_profit_loss == Decimal("1470")


def test_multiple_assets_portfolio_performance(
    db_session,
):
    user = create_user(
        db_session,
        "portfolio_performance_multiple@example.com",
    )

    infy = create_asset(db_session)

    tcs = create_asset(
        db_session,
        symbol="TCS",
        name="Tata Consultancy Services",
    )

    create_transaction(
        db_session=db_session,
        user_id=user.id,
        asset_id=infy.id,
        transaction_type=TransactionType.BUY,
        quantity=Decimal("100"),
        price=Decimal("50"),
        amount=Decimal("5000"),
        charges=Decimal("20"),
    )

    create_transaction(
        db_session=db_session,
        user_id=user.id,
        asset_id=tcs.id,
        transaction_type=TransactionType.BUY,
        quantity=Decimal("50"),
        price=Decimal("100"),
        amount=Decimal("5000"),
        charges=Decimal("20"),
    )

    create_market_price(
        db_session,
        infy.id,
        Decimal("60"),
    )

    create_market_price(
        db_session,
        tcs.id,
        Decimal("120"),
    )

    service = create_service(db_session)

    result = service.get_performance(
        user_id=user.id,
    )

    assert result.total_invested == Decimal("10040")
    assert result.total_market_value == Decimal("12000")

    assert (
        result.total_realized_profit_loss
        == Decimal("0")
    )

    assert (
        result.total_unrealized_profit_loss
        == Decimal("1960")
    )

    assert result.total_profit_loss == Decimal("1960")


def test_portfolio_performance_without_market_price(
    db_session,
):
    user = create_user(
        db_session,
        "portfolio_performance_no_price@example.com",
    )

    asset = create_asset(db_session)

    create_transaction(
        db_session=db_session,
        user_id=user.id,
        asset_id=asset.id,
        transaction_type=TransactionType.BUY,
        quantity=Decimal("100"),
        price=Decimal("50"),
        amount=Decimal("5000"),
        charges=Decimal("20"),
    )

    service = create_service(db_session)

    result = service.get_performance(
        user_id=user.id,
    )

    assert result.total_invested == Decimal("5020")
    assert result.total_market_value == Decimal("0")

    assert (
        result.total_realized_profit_loss
        == Decimal("0")
    )

    assert (
        result.total_unrealized_profit_loss
        == Decimal("0")
    )

    assert result.total_profit_loss == Decimal("0")
