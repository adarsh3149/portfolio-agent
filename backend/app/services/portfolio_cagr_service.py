from datetime import date
from decimal import Decimal

from app.repositories.portfolio_snapshot_repository import (
    PortfolioSnapshotRepository,
)
from app.services.cagr_service import CAGRService


class PortfolioCAGRService:

    def __init__(
        self,
        repository: PortfolioSnapshotRepository,
    ):
        self.repository = repository
        self.cagr_service = CAGRService()

    def calculate(
        self,
        user_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> Decimal:

        snapshots = self.repository.get_by_user(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )

        if len(snapshots) < 2:
            raise ValueError(
                "At least two portfolio snapshots are required."
            )

        first_snapshot = snapshots[0]
        last_snapshot = snapshots[-1]

        return self.cagr_service.calculate(
            initial_value=(
                first_snapshot.total_market_value
            ),
            final_value=(
                last_snapshot.total_market_value
            ),
            start_date=first_snapshot.snapshot_date,
            end_date=last_snapshot.snapshot_date,
        )
