from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user_model import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=72)


class CreateUserRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=12, max_length=72)
    role: UserRole

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        has_upper = any(ch.isupper() for ch in value)
        has_lower = any(ch.islower() for ch in value)
        has_digit = any(ch.isdigit() for ch in value)
        has_special = any(not ch.isalnum() for ch in value)

        if not all([has_upper, has_lower, has_digit, has_special]):
            raise ValueError(
                "Password must include uppercase, lowercase, number, and special character"
            )
        return value


class UpdateUserRoleRequest(BaseModel):
    role: UserRole


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    role: UserRole


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole
    created_at: datetime
    last_login: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
