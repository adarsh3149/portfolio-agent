from fastapi import APIRouter, Depends

from app.dependencies.services import get_auth_service
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
def register(
    user: UserCreate,
    service: AuthService = Depends(get_auth_service),
):
    return service.register(user)