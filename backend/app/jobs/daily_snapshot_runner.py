from datetime import date

from app.repositories.user_repository import UserRepository
from app.jobs.daily_snapshot_job import DailySnapshotJob


class DailySnapshotRunner:

    def __init__(
        self,
        user_repository: UserRepository,
        snapshot_job: DailySnapshotJob,
    ):
        self.user_repository = user_repository
        self.snapshot_job = snapshot_job

    def run(
        self,
        snapshot_date: date,
    ):

        users = self.user_repository.get_all()

        snapshots = []

        for user in users:
            snapshot = self.snapshot_job.run(
                user_id=user.id,
                snapshot_date=snapshot_date,
            )

            snapshots.append(snapshot)

        return snapshots
