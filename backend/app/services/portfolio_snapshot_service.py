from datetime import date

from app.models.portfolio_snapshot import PortfolioSnapshot
from app.repositories.portfolio_snapshot_repository import (
    PortfolioSnapshotRepository,
)
from app.services.portfolio_performance_service import (
    PortfolioPerformanceService,
)


class PortfolioSnapshotService:

    def __init__(
        self,
        performance_service: PortfolioPerformanceService,
        repository: PortfolioSnapshotRepository,
    ):
        self.performance_service = performance_service
        self.repository = repository

    def create_snapshot(
        self,
        user_id: int,
        snapshot_date: date,
    ) -> PortfolioSnapshot:

        performance = (
            self.performance_service.get_performance(
                user_id=user_id,
            )
        )

        existing_snapshot = (
            self.repository.get_by_user_and_date(
                user_id=user_id,
                snapshot_date=snapshot_date,
            )
        )

        if existing_snapshot is not None:
            existing_snapshot.total_invested = (
                performance.total_invested
            )

            existing_snapshot.total_market_value = (
                performance.total_market_value
            )

            existing_snapshot.total_realized_profit_loss = (
                performance.total_realized_profit_loss
            )

            existing_snapshot.total_unrealized_profit_loss = (
                performance.total_unrealized_profit_loss
            )

            existing_snapshot.total_profit_loss = (
                performance.total_profit_loss
            )

            self.repository.db.commit()
            self.repository.db.refresh(
                existing_snapshot
            )

            return existing_snapshot

        snapshot = PortfolioSnapshot(
            user_id=user_id,
            snapshot_date=snapshot_date,
            total_invested=performance.total_invested,
            total_market_value=performance.total_market_value,
            total_realized_profit_loss=(
                performance.total_realized_profit_loss
            ),
            total_unrealized_profit_loss=(
                performance.total_unrealized_profit_loss
            ),
            total_profit_loss=performance.total_profit_loss,
        )

        return self.repository.create(snapshot)

    def get_history(
            self,
            user_id:int,
            start_date: date | None = None,
            end_date: date | None = None,
    ) -> list[PortfolioSnapshot]:

        if (
            start_date is not None
            and end_date is not None
            and start_date > end_date
        ):
            raise ValueError(
                "start_date cannot be greater than end_date"
            )
        

        return self.repository.get_by_user(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )
