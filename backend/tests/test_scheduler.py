from unittest.mock import Mock

from app.scheduler.scheduler import PortfolioScheduler


def test_scheduler_registers_daily_snapshot_job():
    scheduler = Mock()
    daily_snapshot_runner = Mock()

    portfolio_scheduler = PortfolioScheduler(
        scheduler=scheduler,
        daily_snapshot_runner=daily_snapshot_runner,
    )

    portfolio_scheduler.register_jobs()

    scheduler.add_job.assert_called_once()

    args, kwargs = scheduler.add_job.call_args

    assert args[0] == daily_snapshot_runner
    assert kwargs["trigger"] == "cron"
    assert kwargs["hour"] == 0
    assert kwargs["minute"] == 5


def test_scheduler_does_not_run_job_during_registration():
    scheduler = Mock()
    daily_snapshot_runner = Mock()

    portfolio_scheduler = PortfolioScheduler(
        scheduler=scheduler,
        daily_snapshot_runner=daily_snapshot_runner,
    )

    portfolio_scheduler.register_jobs()

    daily_snapshot_runner.assert_not_called()


def test_scheduler_register_jobs_returns_scheduler():
    scheduler = Mock()
    daily_snapshot_runner = Mock()

    portfolio_scheduler = PortfolioScheduler(
        scheduler=scheduler,
        daily_snapshot_runner=daily_snapshot_runner,
    )

    result = portfolio_scheduler.register_jobs()

    assert result is scheduler
