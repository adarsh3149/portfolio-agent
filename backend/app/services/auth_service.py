from fastapi import HTTPException, status

from app.core.security import (
    hash_password,
    create_access_token,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class AuthService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register(self, data: UserCreate) -> User:

        existing = self.repository.get_by_email(data.email)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered."
            )

        user = User(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password)
        )

        return self.repository.create(user)

    def login(
        self,
        email: str,
        password: str,
    ) -> str:

        user = self.repository.get_by_email(email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return create_access_token(
            str(user.id)
        )