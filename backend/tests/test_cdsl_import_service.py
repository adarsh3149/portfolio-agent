from datetime import datetime
from decimal import Decimal

from app.schemas.cdsl import (
    CDSLTransactionDirection,
    CDSLTransactionEvent,
)
from app.services.cdsl.import_service import (
    CDSLImportService,
)


class FakeParser:

    def __init__(
        self,
        events,
    ):
        self.events = events

    def parse(
        self,
        email_body: str,
    ):
        return self.events


class FakeRepository:

    def __init__(
        self,
        existing_events=None,
    ):
        self.existing_events = (
            existing_events or {}
        )
        self.created_events = []

    def get_by_source_reference(
        self,
        user_id: int,
        source: str,
        source_reference: str,
    ):
        return self.existing_events.get(
            (
                user_id,
                source,
                source_reference,
            )
        )

    def create(
        self,
        event,
    ):
        self.created_events.append(event)
        return event


def create_event(
    isin: str = "INF843K01AO4",
    quantity: Decimal = Decimal("0.771"),
    direction: CDSLTransactionDirection = (
        CDSLTransactionDirection.CREDIT
    ),
):
    return CDSLTransactionEvent(
        security_name="Edelweiss Mid Cap Fund",
        isin=isin,
        quantity=quantity,
        direction=direction,
        transaction_datetime=datetime(
            2026,
            8,
            10,
            23,
            17,
            3,
        ),
        source="CDSL",
    )


def test_imports_new_events():

    event = create_event()

    parser = FakeParser(
        [event],
    )

    repository = FakeRepository()

    service = CDSLImportService(
        parser=parser,
        repository=repository,
    )

    result = service.import_email(
        user_id=10,
        email_body="test email",
    )

    assert result.total_events == 1
    assert result.imported == 1
    assert result.duplicates == 0

    assert len(repository.created_events) == 1

    saved_event = repository.created_events[0]

    assert saved_event.user_id == 10
    assert saved_event.isin == "INF843K01AO4"
    assert saved_event.quantity == Decimal("0.771")
    assert saved_event.direction == (
        CDSLTransactionDirection.CREDIT
    )


def test_imports_multiple_events():

    event_1 = create_event(
        isin="INF843K01AO4",
        quantity=Decimal("0.771"),
    )

    event_2 = create_event(
        isin="INF205K013T3",
        quantity=Decimal("1.847"),
    )

    parser = FakeParser(
        [event_1, event_2],
    )

    repository = FakeRepository()

    service = CDSLImportService(
        parser=parser,
        repository=repository,
    )

    result = service.import_email(
        user_id=10,
        email_body="test email",
    )

    assert result.total_events == 2
    assert result.imported == 2
    assert result.duplicates == 0

    assert len(repository.created_events) == 2


def test_duplicate_events_are_not_imported():

    event = create_event()

    parser = FakeParser(
        [event],
    )

    service_reference = (
        f"{event.isin}|"
        f"{event.quantity}|"
        f"{event.direction.value}|"
        f"{event.transaction_datetime.isoformat()}"
    )

    existing_event = object()

    repository = FakeRepository(
        existing_events={
            (
                10,
                "CDSL",
                service_reference,
            ): existing_event,
        },
    )

    service = CDSLImportService(
        parser=parser,
        repository=repository,
    )

    result = service.import_email(
        user_id=10,
        email_body="test email",
    )

    assert result.total_events == 1
    assert result.imported == 0
    assert result.duplicates == 1

    assert repository.created_events == []


def test_mixed_new_and_duplicate_events():

    event_1 = create_event(
        isin="INF843K01AO4",
    )

    event_2 = create_event(
        isin="INF205K013T3",
        quantity=Decimal("1.847"),
    )

    duplicate_reference = (
        f"{event_1.isin}|"
        f"{event_1.quantity}|"
        f"{event_1.direction.value}|"
        f"{event_1.transaction_datetime.isoformat()}"
    )

    parser = FakeParser(
        [event_1, event_2],
    )

    repository = FakeRepository(
        existing_events={
            (
                10,
                "CDSL",
                duplicate_reference,
            ): object(),
        },
    )

    service = CDSLImportService(
        parser=parser,
        repository=repository,
    )

    result = service.import_email(
        user_id=10,
        email_body="test email",
    )

    assert result.total_events == 2
    assert result.imported == 1
    assert result.duplicates == 1

    assert len(repository.created_events) == 1
    assert (
        repository.created_events[0].isin
        == "INF205K013T3"
    )


def test_import_is_user_specific():

    event = create_event()

    parser = FakeParser(
        [event],
    )

    repository = FakeRepository()

    service = CDSLImportService(
        parser=parser,
        repository=repository,
    )

    result = service.import_email(
        user_id=42,
        email_body="test email",
    )

    assert result.imported == 1

    saved_event = repository.created_events[0]

    assert saved_event.user_id == 42
