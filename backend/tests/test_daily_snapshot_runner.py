from datetime import date
from unittest.mock import Mock

from app.jobs.daily_snapshot_runner import (
    DailySnapshotRunner,
)


def test_runner_creates_snapshot_for_every_user():
    user_repository = Mock()
    snapshot_job = Mock()

    user_1 = Mock(id=1)
    user_2 = Mock(id=2)
    user_3 = Mock(id=3)

    user_repository.get_all.return_value = [
        user_1,
        user_2,
        user_3,
    ]

    snapshot_job.run.side_effect = [
        "snapshot-1",
        "snapshot-2",
        "snapshot-3",
    ]

    runner = DailySnapshotRunner(
        user_repository=user_repository,
        snapshot_job=snapshot_job,
    )

    result = runner.run(
        snapshot_date=date(2026, 8, 10),
    )

    assert result == [
        "snapshot-1",
        "snapshot-2",
        "snapshot-3",
    ]

    user_repository.get_all.assert_called_once()

    assert snapshot_job.run.call_count == 3

    snapshot_job.run.assert_any_call(
        user_id=1,
        snapshot_date=date(2026, 8, 10),
    )

    snapshot_job.run.assert_any_call(
        user_id=2,
        snapshot_date=date(2026, 8, 10),
    )

    snapshot_job.run.assert_any_call(
        user_id=3,
        snapshot_date=date(2026, 8, 10),
    )


def test_runner_uses_same_snapshot_date_for_all_users():
    user_repository = Mock()
    snapshot_job = Mock()

    user_repository.get_all.return_value = [
        Mock(id=10),
        Mock(id=20),
    ]

    runner = DailySnapshotRunner(
        user_repository=user_repository,
        snapshot_job=snapshot_job,
    )

    snapshot_date = date(2026, 8, 15)

    runner.run(
        snapshot_date=snapshot_date,
    )

    assert snapshot_job.run.call_count == 2

    snapshot_job.run.assert_any_call(
        user_id=10,
        snapshot_date=snapshot_date,
    )

    snapshot_job.run.assert_any_call(
        user_id=20,
        snapshot_date=snapshot_date,
    )


def test_runner_returns_empty_list_when_no_users_exist():
    user_repository = Mock()
    snapshot_job = Mock()

    user_repository.get_all.return_value = []

    runner = DailySnapshotRunner(
        user_repository=user_repository,
        snapshot_job=snapshot_job,
    )

    result = runner.run(
        snapshot_date=date(2026, 8, 10),
    )

    assert result == []

    user_repository.get_all.assert_called_once()

    snapshot_job.run.assert_not_called()
