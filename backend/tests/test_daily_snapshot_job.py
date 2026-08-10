from datetime import date
from unittest.mock import Mock

from app.jobs.daily_snapshot_job import DailySnapshotJob


def test_daily_snapshot_job_creates_snapshot_for_user():
    snapshot_service = Mock()

    job = DailySnapshotJob(
        snapshot_service=snapshot_service,
    )

    job.run(
        user_id=1,
        snapshot_date=date(2026, 8, 10),
    )

    snapshot_service.create_snapshot.assert_called_once_with(
        user_id=1,
        snapshot_date=date(2026, 8, 10),
    )


def test_daily_snapshot_job_passes_snapshot_date_unchanged():
    snapshot_service = Mock()

    job = DailySnapshotJob(
        snapshot_service=snapshot_service,
    )

    snapshot_date = date(2026, 8, 10)

    job.run(
        user_id=42,
        snapshot_date=snapshot_date,
    )

    snapshot_service.create_snapshot.assert_called_once_with(
        user_id=42,
        snapshot_date=snapshot_date,
    )


def test_daily_snapshot_job_returns_created_snapshot():
    snapshot_service = Mock()

    expected_snapshot = object()

    snapshot_service.create_snapshot.return_value = (
        expected_snapshot
    )

    job = DailySnapshotJob(
        snapshot_service=snapshot_service,
    )

    result = job.run(
        user_id=1,
        snapshot_date=date(2026, 8, 10),
    )

    assert result is expected_snapshot
