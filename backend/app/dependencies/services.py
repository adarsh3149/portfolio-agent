from fastapi import Depends

from app.dependencies.repositories import get_user_repository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


def get_auth_service(
    repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(repository)