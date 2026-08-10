from apscheduler.schedulers.background import (
    BackgroundScheduler,
)

from app.scheduler.bootstrap import create_scheduler


def test_create_scheduler_returns_background_scheduler():
    scheduler = create_scheduler()

    assert isinstance(
        scheduler,
        BackgroundScheduler,
    )


def test_create_scheduler_registers_daily_snapshot_job():
    scheduler = create_scheduler()

    jobs = scheduler.get_jobs()

    assert len(jobs) == 1

    job = jobs[0]

    fields = {
        field.name: field
        for field in job.trigger.fields
    }

    assert fields["hour"].expressions[0].first == 0
    assert fields["minute"].expressions[0].first == 5