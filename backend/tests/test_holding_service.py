from decimal import Decimal

import pytest

from app.enums import TransactionType
from app.services.holding_accumulator import HoldingAccumulator
from app.services.holding_service import HoldingService


# -------------------------------------------------------------------
# Fake Objects
# -------------------------------------------------------------------

class FakeAsset:
    id = 1
    symbol = "INFY"
    name = "Infosys"


class FakeTransaction:
    quantity = Decimal("100")
    amount = Decimal("5000")
    charges = Decimal("0")


class FakeTransactionBase:

    def __init__(self):
        self.asset_id = 1
        self.asset = FakeAsset()


class FakeBuyTransaction(FakeTransactionBase):

    def __init__(self, quantity, amount):
        super().__init__()

        self.transaction_type = TransactionType.BUY
        self.quantity = quantity
        self.amount = amount
        self.charges = Decimal("0")


class FakeSellTransaction(FakeTransactionBase):

    def __init__(self, quantity):
        super().__init__()

        self.transaction_type = TransactionType.SELL
        self.quantity = quantity


class FakeRepository:

    def get_by_user(self, user_id: int):
        return [
            FakeBuyTransaction(
                quantity=Decimal("100"),
                amount=Decimal("5000"),
            ),
            FakeBuyTransaction(
                quantity=Decimal("50"),
                amount=Decimal("3000"),
            ),
            FakeSellTransaction(
                quantity=Decimal("30"),
            ),
        ]


# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------

def test_process_buy():

    service = HoldingService(None)

    state = HoldingAccumulator(
        asset_id=1,
        symbol="INFY",
        asset_name="Infosys",
    )

    service._process_buy(
        state,
        FakeTransaction(),
    )

    assert state.units == Decimal("100")
    assert state.invested_amount == Decimal("5000")


def test_process_sell():

    service = HoldingService(None)

    state = HoldingAccumulator(
        asset_id=1,
        symbol="INFY",
        asset_name="Infosys",
        units=Decimal("150"),
        invested_amount=Decimal("8000"),
    )

    service._process_sell(
        state,
        FakeSellTransaction(
            quantity=Decimal("30"),
        ),
    )

    assert state.units == Decimal("120")
    assert state.invested_amount == Decimal("6400")


def test_sell_more_than_owned():

    service = HoldingService(None)

    state = HoldingAccumulator(
        asset_id=1,
        symbol="INFY",
        asset_name="Infosys",
        units=Decimal("10"),
        invested_amount=Decimal("500"),
    )

    transaction = FakeSellTransaction(
        quantity=Decimal("20"),
    )

    with pytest.raises(ValueError):
        service._process_sell(
            state,
            transaction,
        )


def test_get_holdings():

    repository = FakeRepository()

    service = HoldingService(repository)

    holdings = service.get_holdings(user_id=1)

    assert len(holdings) == 1

    holding = holdings[0]

    assert holding.asset_id == 1
    assert holding.symbol == "INFY"
    assert holding.asset_name == "Infosys"

    assert holding.units == Decimal("120")
    assert holding.invested_amount == Decimal("6400")

    assert (
        holding.average_cost.quantize(
            Decimal("0.0001")
        )
        == Decimal("53.3333")
    )