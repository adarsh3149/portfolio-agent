from unittest.mock import Mock, patch

from app.scheduler.main import start_scheduler


@patch("app.scheduler.main.create_scheduler")
def test_start_scheduler_creates_and_starts_scheduler(
    create_scheduler,
):
    scheduler = Mock()
    create_scheduler.return_value = scheduler

    result = start_scheduler()

    create_scheduler.assert_called_once()
    scheduler.start.assert_called_once()

    assert result is scheduler
