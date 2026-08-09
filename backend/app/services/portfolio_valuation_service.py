from decimal import Decimal

from app.repositories.market_price_repository import (
    MarketPriceRepository,
)
from app.services.holding_service import HoldingService
from app.schemas.portfolio_valuation import PortfolioValuation


class PortfolioValuationService:

    def __init__(
        self,
        holding_service: HoldingService,
        market_price_repository: MarketPriceRepository,
    ):
        self.holding_service = holding_service
        self.market_price_repository = market_price_repository

    def get_valuations(
        self,
        user_id: int,
    ) -> list[PortfolioValuation]:

        holdings = self.holding_service.get_holdings(
            user_id
        )

        valuations = []

        for holding in holdings:

            if holding.units <= 0:
                continue

            market_price = (
                self.market_price_repository
                .get_latest_by_asset(
                    holding.asset_id
                )
            )

            if market_price is None:
                continue

            current_price = market_price.price

            market_value = (
                holding.units *
                current_price
            )

            unrealized_profit_loss = (
                market_value -
                holding.invested_amount
            )

            unrealized_profit_loss_percentage = (
                (
                    unrealized_profit_loss /
                    holding.invested_amount
                ) * Decimal("100")
                if holding.invested_amount > 0
                else Decimal("0")
            )

            valuations.append(
                PortfolioValuation(
                    asset_id=holding.asset_id,
                    symbol=holding.symbol,
                    units=holding.units,
                    invested_amount=holding.invested_amount,
                    current_price=current_price,
                    market_value=market_value,
                    unrealized_profit_loss=(
                        unrealized_profit_loss
                    ),
                    unrealized_profit_loss_percentage=(
                        unrealized_profit_loss_percentage
                    ),
                )
            )

        return valuations
