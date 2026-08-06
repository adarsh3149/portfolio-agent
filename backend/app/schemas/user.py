from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        description="Full name of the user"
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
        description="Plain text password"
    )


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)