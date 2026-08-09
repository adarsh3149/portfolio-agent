from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.dependencies.services import (
    get_portfolio_valuation_service,
)
from app.models.user import User
from app.schemas.portfolio_valuation import (
    PortfolioValuation,
)
from app.services.portfolio_valuation_service import (
    PortfolioValuationService,
)


router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"],
)


@router.get(
    "/valuation",
    response_model=list[PortfolioValuation],
)
def get_portfolio_valuation(
    service: PortfolioValuationService = Depends(
        get_portfolio_valuation_service,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
):
    return service.get_valuations(
        user_id=current_user.id,
    )
