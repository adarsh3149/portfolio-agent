from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.dependencies.services import get_market_data_service
from app.schemas.market_price import MarketPriceResponse
from app.models.user import User
from app.services.market_data_service import MarketDataService


router = APIRouter(
    prefix="/market-data",
    tags=["Market Data"],
)


@router.post(
    "/assets/{asset_id}/price",
    response_model=MarketPriceResponse,
    status_code=201,
)
def fetch_asset_price(
    asset_id: int,
    service: MarketDataService = Depends(
        get_market_data_service,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
):
    return service.fetch_and_store_price(
        asset_id
    )
