from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.portfolio_snapshot import PortfolioSnapshot


class PortfolioSnapshotRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        snapshot: PortfolioSnapshot,
    ) -> PortfolioSnapshot:

        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)

        return snapshot

    def get_by_user_and_date(
        self,
        user_id: int,
        snapshot_date: date,
    ) -> PortfolioSnapshot | None:

        statement = (
            select(PortfolioSnapshot)
            .where(
                PortfolioSnapshot.user_id == user_id,
                PortfolioSnapshot.snapshot_date
                == snapshot_date,
            )
        )

        return self.db.scalar(statement)

    def get_by_user(
        self,
        user_id: int,
    ) -> list[PortfolioSnapshot]:

        statement = (
            select(PortfolioSnapshot)
            .where(
                PortfolioSnapshot.user_id == user_id,
            )
            .order_by(
                PortfolioSnapshot.snapshot_date,
            )
        )

        return list(
            self.db.scalars(statement)
        )
