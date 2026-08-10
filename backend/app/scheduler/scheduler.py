from typing import Any


class PortfolioScheduler:
    def __init__(
        self,
        scheduler: Any,
        daily_snapshot_runner,
    ):
        self.scheduler = scheduler
        self.daily_snapshot_runner = daily_snapshot_runner

    def register_jobs(self):
        self.scheduler.add_job(
            self.daily_snapshot_runner,
            trigger="cron",
            hour=0,
            minute=5,
        )

        return self.scheduler