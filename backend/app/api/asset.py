from fastapi import APIRouter, Depends, status

from app.dependencies.services import get_asset_service
from app.schemas.asset import (
    AssetCreate,
    AssetResponse,
)
from app.services.asset_service import AssetService

router = APIRouter(
    prefix="/assets",
    tags=["Assets"],
)

@router.post(
    "",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_asset(
    request: AssetCreate,
    service: AssetService = Depends(
        get_asset_service,
    ),
):
    return service.create_asset(request)

@router.get(
    "",
    response_model=list[AssetResponse],
)
def get_assets(
    service: AssetService = Depends(
        get_asset_service,
    ),
):
    return service.get_assets()

@router.get(
    "/{asset_id}",
    response_model=AssetResponse,
)
def get_asset(
    asset_id: int,
    service: AssetService = Depends(
        get_asset_service,
    ),
):
    return service.get_asset(asset_id)

