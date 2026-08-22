from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.dependencies.services import (
    get_cdsl_import_service,
    get_cdsl_transaction_processor,
)
from app.models.user import User
from app.schemas.transaction import TransactionResponse
from app.services.cdsl.import_service import (
    CDSLImportService,
    CDSLImportResult,
)
from app.services.cdsl.transaction_processor import (
    CDSLTransactionProcessor,
)

router = APIRouter(
    prefix="/cdsl",
    tags=["CDSL"],
)


@router.post(
    "/import",
    response_model=CDSLImportResult,
)
def import_cdsl_email(
    email_body: str,
    current_user: User = Depends(
        get_current_user,
    ),
    service: CDSLImportService = Depends(
        get_cdsl_import_service,
    ),
):
    return service.import_email(
        user_id=current_user.id,
        email_body=email_body,
    )


@router.post(
    "/process",
    response_model=list[TransactionResponse],
)
def process_pending_cdsl_events(
    current_user: User = Depends(
        get_current_user,
    ),
    processor: CDSLTransactionProcessor = Depends(
        get_cdsl_transaction_processor,
    ),
):
    return processor.process_unprocessed_events(
        user_id=current_user.id,
    )
