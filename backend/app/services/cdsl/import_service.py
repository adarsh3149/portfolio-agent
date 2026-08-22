from dataclasses import dataclass

from app.models.cdsl_transaction_event import (
    CDSLTransactionEvent,
)
from app.repositories.cdsl_transaction_event_repository import (
    CDSLTransactionEventRepository,
)
from app.services.cdsl.daily_email_parser import (
    CDSLDailyEmailParser,
)


@dataclass(frozen=True)
class CDSLImportResult:
    total_events: int
    imported: int
    duplicates: int


class CDSLImportService:

    def __init__(
        self,
        parser: CDSLDailyEmailParser,
        repository: CDSLTransactionEventRepository,
    ):
        self.parser = parser
        self.repository = repository

    def import_email(
        self,
        user_id: int,
        email_body: str,
    ) -> CDSLImportResult:

        events = self.parser.parse(
            email_body,
        )

        imported = 0
        duplicates = 0

        for event in events:

            source_reference = (
                self._build_source_reference(event)
            )

            existing_event = (
                self.repository.get_by_source_reference(
                    user_id=user_id,
                    source=event.source,
                    source_reference=source_reference,
                )
            )

            if existing_event is not None:
                duplicates += 1
                continue

            persisted_event = CDSLTransactionEvent(
                user_id=user_id,
                security_name=event.security_name,
                isin=event.isin,
                quantity=event.quantity,
                direction=event.direction,
                transaction_datetime=(
                    event.transaction_datetime
                ),
                source=event.source,
                source_reference=source_reference,
            )

            self.repository.create(
                persisted_event,
            )

            imported += 1

        return CDSLImportResult(
            total_events=len(events),
            imported=imported,
            duplicates=duplicates,
        )

    @staticmethod
    def _build_source_reference(
        event,
    ) -> str:

        return (
            f"{event.isin}|"
            f"{event.quantity}|"
            f"{event.direction.value}|"
            f"{event.transaction_datetime.isoformat()}"
        )
