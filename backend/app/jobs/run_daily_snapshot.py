from datetime import date

from app.database.session import SessionLocal
from app.factories.services import (
    create_portfolio_performance_service,
)
from app.jobs.daily_snapshot_job import DailySnapshotJob
from app.jobs.daily_snapshot_runner import DailySnapshotRunner
from app.repositories.portfolio_snapshot_repository import (
    PortfolioSnapshotRepository,
)
from app.repositories.user_repository import UserRepository
from app.services.portfolio_snapshot_service import (
    PortfolioSnapshotService,
)

from sqlalchemy.orm import Session


def run_daily_snapshot(
    snapshot_date: date | None = None,
    db: Session | None = None,
):
    if snapshot_date is None:
        snapshot_date = date.today()

    owns_session = db is None

    if owns_session:
        db = SessionLocal()

    try:
        user_repository = UserRepository(db)

        snapshot_repository = PortfolioSnapshotRepository(
            db
        )

        performance_service = (
            create_portfolio_performance_service(db)
        )

        snapshot_service = PortfolioSnapshotService(
            performance_service=performance_service,
            repository=snapshot_repository,
        )

        snapshot_job = DailySnapshotJob(
            snapshot_service=snapshot_service,
        )

        runner = DailySnapshotRunner(
            user_repository=user_repository,
            snapshot_job=snapshot_job,
        )

        return runner.run(
            snapshot_date=snapshot_date,
        )

    finally:
        if owns_session:
            db.close()