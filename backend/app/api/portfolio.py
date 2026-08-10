from fastapi import APIRouter
from fastapi import Depends

from app.dependencies.auth import get_current_user
from app.dependencies.services import get_holding_service
from app.models.user import User
from app.schemas.holding import Holding
from app.services.holding_service import HoldingService
from app.dependencies.services import get_portfolio_service
from app.schemas.portfolio import PortfolioSummary
from app.services.portfolio_service import PortfolioService

from app.dependencies.services import (
    get_portfolio_performance_service,
)
from app.schemas.portfolio_performance import (
    PortfolioPerformance,
)
from app.services.portfolio_performance_service import (
    PortfolioPerformanceService,
)

router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"],
)

@router.get(
    "/holdings",
    response_model=list[Holding],
)
def get_holdings(
    current_user: User = Depends(get_current_user),
    service: HoldingService = Depends(get_holding_service),
):
    return service.get_holdings(
        current_user.id,
    )

@router.get(
    "/summary",
    response_model=PortfolioSummary,
)
def get_summary(
    current_user: User = Depends(get_current_user),
    service: PortfolioService = Depends(
        get_portfolio_service,
    ),
):
    return service.get_summary(
        current_user.id,
    )

@router.get(
    "/performance",
    response_model=PortfolioPerformance,
)
def get_performance(
    current_user: User = Depends(get_current_user),
    service: PortfolioPerformanceService = Depends(
        get_portfolio_performance_service,
    ),
):
    return service.get_performance(
        current_user.id,
    )
