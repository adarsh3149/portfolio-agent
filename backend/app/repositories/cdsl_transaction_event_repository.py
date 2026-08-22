from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cdsl_transaction_event import (
    CDSLTransactionEvent,
)


class CDSLTransactionEventRepository:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    def create(
        self,
        event: CDSLTransactionEvent,
    ) -> CDSLTransactionEvent:

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        return event

    def get_by_source_reference(
        self,
        user_id: int,
        source: str,
        source_reference: str,
    ) -> CDSLTransactionEvent | None:

        statement = (
            select(CDSLTransactionEvent)
            .where(
                CDSLTransactionEvent.user_id == user_id,
                CDSLTransactionEvent.source == source,
                CDSLTransactionEvent.source_reference
                == source_reference,
            )
        )

        return self.db.scalar(statement)

    def get_by_user(
        self,
        user_id: int,
    ) -> list[CDSLTransactionEvent]:

        statement = (
            select(CDSLTransactionEvent)
            .where(
                CDSLTransactionEvent.user_id == user_id,
            )
            .order_by(
                CDSLTransactionEvent.transaction_datetime,
                CDSLTransactionEvent.id,
            )
        )

        return list(
            self.db.scalars(statement)
        )
        
    def get_unprocessed_by_user(
        self,
        user_id:int, 
    ) -> list[CDSLTransactionEvent] :
        statement = (
            select(CDSLTransactionEvent)
            .where(
                CDSLTransactionEvent.user_id == user_id,
                CDSLTransactionEvent.processed.is_(False),
            )
            .order_by(
                CDSLTransactionEvent.transaction_datetime,
                CDSLTransactionEvent.id,
            )
        )

        return list(
            self.db.scalars(statement)
        )
        
    def mark_processed(
        self,
        event: CDSLTransactionEvent,
    ) -> CDSLTransactionEvent:

        event.processed = True

        self.db.commit()
        self.db.refresh(event)

        return event
