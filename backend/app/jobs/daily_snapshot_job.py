from datetime import date

from app.models.portfolio_snapshot import PortfolioSnapshot
from app.services.portfolio_snapshot_service import (
    PortfolioSnapshotService,
)


class DailySnapshotJob:

    def __init__(
        self,
        snapshot_service: PortfolioSnapshotService,
    ):
        self.snapshot_service = snapshot_service

    def run(
        self,
        user_id: int,
        snapshot_date: date,
    ) -> PortfolioSnapshot:

        return self.snapshot_service.create_snapshot(
            user_id=user_id,
            snapshot_date=snapshot_date,
        )
