from apscheduler.schedulers.background import (
    BackgroundScheduler,
)

from app.jobs.run_daily_snapshot import (
    run_daily_snapshot,
)
from app.scheduler.scheduler import PortfolioScheduler


def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()

    portfolio_scheduler = PortfolioScheduler(
        scheduler=scheduler,
        daily_snapshot_runner=run_daily_snapshot,
    )

    portfolio_scheduler.register_jobs()

    return scheduler
