from datetime import date
from decimal import Decimal

from app.enums import TransactionType
from app.models.asset import Asset
from app.models.transaction import Transaction
from app.models.user import User
from app.repositories.transaction_repository import (
    TransactionRepository,
)
from app.services.performance_service import PerformanceService


def create_user(
    db_session,
    email: str,
):
    user = User(
        name="Performance Test User",
        email=email,
        password_hash="test-password",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def create_asset(
    db_session,
):
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


def create_service(db_session):
    repository = TransactionRepository(
        db_session
    )

    return PerformanceService(
        repository=repository,
    )


def test_buy_only_has_zero_realized_profit_loss(
    db_session,
):
    user = create_user(
        db_session,
        "performance_buy@example.com",
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

    result = service.get_realized_profit_loss(
        user_id=user.id,
    )

    assert result == Decimal("0")


def test_buy_then_sell_calculates_realized_profit_loss(
    db_session,
):
    user = create_user(
        db_session,
        "performance_sell@example.com",
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

    service = create_service(db_session)

    result = service.get_realized_profit_loss(
        user_id=user.id,
    )

    # Buy cost:
    # 5000 + 20 = 5020
    #
    # Average cost:
    # 5020 / 100 = 50.20
    #
    # Cost basis of 50 sold:
    # 50 * 50.20 = 2510
    #
    # Realized P/L:
    # 3500 - 2510 - 10 = 980

    assert result == Decimal("980")


def test_multiple_buys_use_average_cost_for_realized_profit_loss(
    db_session,
):
    user = create_user(
        db_session,
        "performance_multiple_buys@example.com",
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
        transaction_type=TransactionType.BUY,
        quantity=Decimal("100"),
        price=Decimal("60"),
        amount=Decimal("6000"),
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

    service = create_service(db_session)

    result = service.get_realized_profit_loss(
        user_id=user.id,
    )

    # Total cost:
    # 5020 + 6020 = 11040
    #
    # Total units:
    # 200
    #
    # Average cost:
    # 11040 / 200 = 55.20
    #
    # Cost basis of 50 sold:
    # 50 * 55.20 = 2760
    #
    # Realized P/L:
    # 3500 - 2760 - 10 = 730

    assert result == Decimal("730")

def test_partial_sell_uses_remaining_average_cost(
    db_session,
):
    user = create_user(
        db_session,
        "performance_partial_sell@example.com",
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

    # First partial sell
    create_transaction(
        db_session=db_session,
        user_id=user.id,
        asset_id=asset.id,
        transaction_type=TransactionType.SELL,
        quantity=Decimal("25"),
        price=Decimal("70"),
        amount=Decimal("1750"),
        charges=Decimal("5"),
    )

    # Second partial sell
    create_transaction(
        db_session=db_session,
        user_id=user.id,
        asset_id=asset.id,
        transaction_type=TransactionType.SELL,
        quantity=Decimal("25"),
        price=Decimal("80"),
        amount=Decimal("2000"),
        charges=Decimal("5"),
    )

    service = create_service(db_session)

    result = service.get_realized_profit_loss(
        user_id=user.id,
    )

    # Original cost basis:
    # 5020 / 100 = 50.20
    #
    # First sell:
    # 1750 - (25 * 50.20) - 5
    # = 490
    #
    # Second sell:
    # 2000 - (25 * 50.20) - 5
    # = 740
    #
    # Total = 1230

    assert result == Decimal("1230")


def test_complete_sell_realizes_entire_remaining_cost_basis(
    db_session,
):
    user = create_user(
        db_session,
        "performance_complete_sell@example.com",
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
        quantity=Decimal("100"),
        price=Decimal("70"),
        amount=Decimal("7000"),
        charges=Decimal("10"),
    )

    service = create_service(db_session)

    result = service.get_realized_profit_loss(
        user_id=user.id,
    )

    # Cost basis = 5020
    # Sale proceeds = 7000
    # Sell charges = 10
    # Realized P/L = 1970

    assert result == Decimal("1970")


def test_multiple_assets_have_independent_cost_basis(
    db_session,
):
    user = create_user(
        db_session,
        "performance_multiple_assets@example.com",
    )

    infy = create_asset(db_session)

    tcs = Asset(
        symbol="TCS",
        name="Tata Consultancy Services",
        asset_type="STOCK",
        exchange="NSE",
        currency="INR",
    )

    db_session.add(tcs)
    db_session.commit()
    db_session.refresh(tcs)

    # INFY
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
        asset_id=infy.id,
        transaction_type=TransactionType.SELL,
        quantity=Decimal("50"),
        price=Decimal("70"),
        amount=Decimal("3500"),
        charges=Decimal("10"),
    )

    # TCS
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

    create_transaction(
        db_session=db_session,
        user_id=user.id,
        asset_id=tcs.id,
        transaction_type=TransactionType.SELL,
        quantity=Decimal("25"),
        price=Decimal("120"),
        amount=Decimal("3000"),
        charges=Decimal("10"),
    )

    service = create_service(db_session)

    result = service.get_realized_profit_loss(
        user_id=user.id,
    )

    # INFY:
    # 3500 - 2510 - 10 = 980
    #
    # TCS:
    # Cost = 5020
    # Average = 100.40
    # Sold cost = 25 * 100.40 = 2510
    # 3000 - 2510 - 10 = 480
    #
    # Total = 1460

    assert result == Decimal("1460")


def test_oversell_raises_value_error(
    db_session,
):
    user = create_user(
        db_session,
        "performance_oversell@example.com",
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
        quantity=Decimal("150"),
        price=Decimal("70"),
        amount=Decimal("10500"),
        charges=Decimal("10"),
    )

    service = create_service(db_session)

    try:
        service.get_realized_profit_loss(
            user_id=user.id,
        )
    except ValueError as exc:
        assert str(exc) == (
            "Cannot sell more units than owned."
        )
    else:
        raise AssertionError(
            "Expected ValueError to be raised"
        )
