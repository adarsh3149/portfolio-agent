from decimal import Decimal

from app.services.portfolio_service import PortfolioService


class FakeHolding:

    def __init__(self, invested_amount):
        self.invested_amount = Decimal(invested_amount)


class FakeHoldingService:

    def get_holdings(self, user_id):
        return [
            FakeHolding("5020.00"),
            FakeHolding("10000.00"),
        ]


class FakeTransactionRepository:

    def count_by_user(self, user_id):
        return 5


def test_get_summary():

    holding_service = FakeHoldingService()
    transaction_repository = FakeTransactionRepository()

    service = PortfolioService(
        holding_service=holding_service,
        transaction_repository=transaction_repository,
    )

    summary = service.get_summary(user_id=1)

    assert summary.total_holdings == 2
    assert summary.total_transactions == 5
    assert summary.total_invested == Decimal("15020.00")

class EmptyHoldingService:

    def get_holdings(self, user_id):
        return []


def test_get_summary_empty_portfolio():

    holding_service = EmptyHoldingService()
    transaction_repository = FakeTransactionRepository()

    service = PortfolioService(
        holding_service=holding_service,
        transaction_repository=transaction_repository,
    )

    summary = service.get_summary(user_id=1)

    assert summary.total_holdings == 0
    assert summary.total_transactions == 5
    assert summary.total_invested == Decimal("0.00")