from decimal import Decimal

from app.repositories.market_price_repository import (
    MarketPriceRepository,
)
from app.schemas.portfolio_performance import (
    PortfolioPerformance,
)
from app.services.holding_service import HoldingService
from app.services.performance_service import PerformanceService


class PortfolioPerformanceService:

    def __init__(
        self,
        holding_service: HoldingService,
        performance_service: PerformanceService,
        market_price_repository: MarketPriceRepository,
    ):
        self.holding_service = holding_service
        self.performance_service = performance_service
        self.market_price_repository = market_price_repository

    def get_performance(
        self,
        user_id: int,
    ) -> PortfolioPerformance:

        holdings = self.holding_service.get_holdings(
            user_id
        )

        realized_profit_loss = (
            self.performance_service.get_realized_profit_loss(
                user_id
            )
        )

        total_invested = Decimal("0")
        total_market_value = Decimal("0")
        total_unrealized_profit_loss = Decimal("0")

        for holding in holdings:

            total_invested += holding.invested_amount

            market_price = (
                self.market_price_repository.get_latest_by_asset(
                    holding.asset_id
                )
            )

            if market_price is None:
                continue

            market_value = (
                holding.units
                * market_price.price
            )

            unrealized_profit_loss = (
                market_value
                - holding.invested_amount
            )

            total_market_value += market_value

            total_unrealized_profit_loss += (
                unrealized_profit_loss
            )

        total_profit_loss = (
            realized_profit_loss
            + total_unrealized_profit_loss
        )

        return PortfolioPerformance(
            total_invested=total_invested,
            total_market_value=total_market_value,
            total_realized_profit_loss=(
                realized_profit_loss
            ),
            total_unrealized_profit_loss=(
                total_unrealized_profit_loss
            ),
            total_profit_loss=total_profit_loss,
        )
