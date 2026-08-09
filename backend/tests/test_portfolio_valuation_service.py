from datetime import UTC, datetime
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
from app.services.portfolio_valuation_service import (
    PortfolioValuationService,
)


def test_portfolio_valuation(db_session):

    user = User(
        name="Valuation Test User",
        email="valuation_test@example.com",
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

    transaction_repository = TransactionRepository(
        db_session
    )

    transaction = Transaction(
        user_id=user.id,
        asset_id=asset.id,
        transaction_type=TransactionType.BUY,
        quantity=Decimal("100"),
        price=Decimal("50"),
        amount=Decimal("5000"),
        charges=Decimal("20"),
        transaction_date=datetime(
            2026,
            8,
            9,
            tzinfo=UTC,
        ).date(),
    )

    db_session.add(transaction)
    db_session.commit()

    market_price_repository = MarketPriceRepository(
        db_session
    )

    market_price_repository.create(
        MarketPrice(
            asset_id=asset.id,
            price=Decimal("60"),
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
    )

    holding_service = HoldingService(
        transaction_repository
    )

    service = PortfolioValuationService(
        holding_service=holding_service,
        market_price_repository=market_price_repository,
    )

    result = service.get_valuations(
        user_id=user.id
    )

    assert len(result) == 1

    valuation = result[0]

    assert valuation.asset_id == asset.id
    assert valuation.symbol == "INFY"

    assert valuation.units == Decimal("100")
    assert valuation.invested_amount == Decimal("5020")

    assert valuation.current_price == Decimal("60")

    assert valuation.market_value == Decimal("6000")

    assert (
        valuation.unrealized_profit_loss
        == Decimal("980")
    )

    assert (
        valuation.unrealized_profit_loss_percentage
        == (
            Decimal("980")
            / Decimal("5020")
            * Decimal("100")
        )
    )

def test_valuation_skips_holding_without_market_price(
    db_session,
):

    user = User(
        name="No Price User",
        email="no_price@example.com",
        password_hash="test-password",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    asset = Asset(
        symbol="TCS",
        name="Tata Consultancy Services",
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
        quantity=Decimal("50"),
        price=Decimal("100"),
        amount=Decimal("5000"),
        charges=Decimal("10"),
        transaction_date=datetime(
            2026,
            8,
            9,
            tzinfo=UTC,
        ).date(),
    )

    db_session.add(transaction)
    db_session.commit()

    transaction_repository = TransactionRepository(
        db_session
    )

    market_price_repository = MarketPriceRepository(
        db_session
    )

    holding_service = HoldingService(
        transaction_repository
    )

    service = PortfolioValuationService(
        holding_service=holding_service,
        market_price_repository=market_price_repository,
    )

    result = service.get_valuations(
        user_id=user.id
    )

    assert result == []

def test_valuation_for_multiple_holdings(
    db_session,
):

    user = User(
        name="Multiple Holdings User",
        email="multiple_holdings@example.com",
        password_hash="test-password",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    infy = Asset(
        symbol="INFY",
        name="Infosys",
        asset_type="STOCK",
        exchange="NSE",
        currency="INR",
    )

    tcs = Asset(
        symbol="TCS",
        name="Tata Consultancy Services",
        asset_type="STOCK",
        exchange="NSE",
        currency="INR",
    )

    db_session.add_all([infy, tcs])
    db_session.commit()

    db_session.refresh(infy)
    db_session.refresh(tcs)

    db_session.add_all(
        [
            Transaction(
                user_id=user.id,
                asset_id=infy.id,
                transaction_type=TransactionType.BUY,
                quantity=Decimal("100"),
                price=Decimal("50"),
                amount=Decimal("5000"),
                charges=Decimal("20"),
                transaction_date=datetime(
                    2026,
                    8,
                    9,
                    tzinfo=UTC,
                ).date(),
            ),
            Transaction(
                user_id=user.id,
                asset_id=tcs.id,
                transaction_type=TransactionType.BUY,
                quantity=Decimal("50"),
                price=Decimal("100"),
                amount=Decimal("5000"),
                charges=Decimal("10"),
                transaction_date=datetime(
                    2026,
                    8,
                    9,
                    tzinfo=UTC,
                ).date(),
            ),
        ]
    )

    db_session.commit()

    market_price_repository = MarketPriceRepository(
        db_session
    )

    market_price_repository.create(
        MarketPrice(
            asset_id=infy.id,
            price=Decimal("60"),
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
    )

    market_price_repository.create(
        MarketPrice(
            asset_id=tcs.id,
            price=Decimal("120"),
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
    )

    transaction_repository = TransactionRepository(
        db_session
    )

    holding_service = HoldingService(
        transaction_repository
    )

    service = PortfolioValuationService(
        holding_service=holding_service,
        market_price_repository=market_price_repository,
    )

    result = service.get_valuations(
        user_id=user.id
    )

    assert len(result) == 2

    valuations = {
        valuation.symbol: valuation
        for valuation in result
    }

    assert valuations["INFY"].market_value == Decimal("6000")

    assert valuations["TCS"].market_value == Decimal("6000")

def test_valuation_uses_latest_market_price(
    db_session,
):

    user = User(
        name="Latest Price User",
        email="latest_price@example.com",
        password_hash="test-password",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    asset = Asset(
        symbol="RELIANCE",
        name="Reliance Industries",
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
        price=Decimal("100"),
        amount=Decimal("10000"),
        charges=Decimal("20"),
        transaction_date=datetime(
            2026,
            8,
            9,
            tzinfo=UTC,
        ).date(),
    )

    db_session.add(transaction)
    db_session.commit()

    market_price_repository = MarketPriceRepository(
        db_session
    )

    market_price_repository.create(
        MarketPrice(
            asset_id=asset.id,
            price=Decimal("110"),
            source="test",
            price_time=datetime(
                2026,
                8,
                9,
                10,
                0,
                tzinfo=UTC,
            ),
        )
    )

    market_price_repository.create(
        MarketPrice(
            asset_id=asset.id,
            price=Decimal("125"),
            source="test",
            price_time=datetime(
                2026,
                8,
                9,
                11,
                0,
                tzinfo=UTC,
            ),
        )
    )

    transaction_repository = TransactionRepository(
        db_session
    )

    holding_service = HoldingService(
        transaction_repository
    )

    service = PortfolioValuationService(
        holding_service=holding_service,
        market_price_repository=market_price_repository,
    )

    result = service.get_valuations(
        user_id=user.id
    )

    assert len(result) == 1

    valuation = result[0]

    assert valuation.current_price == Decimal("125")
    assert valuation.market_value == Decimal("12500")
    assert valuation.unrealized_profit_loss == Decimal("2480")