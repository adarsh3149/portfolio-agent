from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date

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

from app.dependencies.services import (
    get_portfolio_snapshot_service,
)

from app.schemas.portfolio_history import (
    PortfolioHistory,
)

from app.services.portfolio_snapshot_service import (
    PortfolioSnapshotService,
)

from app.schemas.portfolio_cagr import PortfolioCAGR
from app.services.portfolio_cagr_service import (
    PortfolioCAGRService,
)
from app.dependencies.services import (
    get_portfolio_cagr_service,
)

from app.services.portfolio_xirr_service import (
    PortfolioXIRRService,
)

from app.dependencies.services import (
    get_portfolio_xirr_service,
)

from app.schemas.portfolio_xirr import PortfolioXIRR

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

@router.get(
    "/history",
    response_model=list[PortfolioHistory],
)
def get_history(
    start_date: date | None = None,
    end_date: date | None = None,
    current_user: User = Depends(get_current_user),
    service: PortfolioSnapshotService = Depends(
        get_portfolio_snapshot_service,
    ),
):
    try:
        return service.get_history(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

@router.get(
    "/cagr",
    response_model=PortfolioCAGR,
)
def get_portfolio_cagr(
    start_date: date | None = Query(
        default=None,
    ),
    end_date: date | None = Query(
        default=None,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    service: PortfolioCAGRService = Depends(
        get_portfolio_cagr_service,
    ),
):
    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "start_date cannot be greater than end_date"
            ),
        )

    try:
        cagr = service.calculate(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return PortfolioCAGR(
        cagr=cagr,
    )

@router.get(
    "/xirr",
    response_model=PortfolioXIRR,
)
def get_portfolio_xirr(
    start_date: date | None = Query(
        default=None,
    ),
    end_date: date | None = Query(
        default=None,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
    service: PortfolioXIRRService = Depends(
        get_portfolio_xirr_service,
    ),
):
    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "start_date cannot be greater than end_date"
            ),
        )

    try:
        xirr = service.calculate(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return PortfolioXIRR(
        xirr=xirr,
    )