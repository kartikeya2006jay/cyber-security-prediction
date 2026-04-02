from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Gov Cyber Threat Detection API"
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(120, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    mongodb_uri: str = Field(..., alias="MONGODB_URI")
    mongodb_db_name: str = Field("cyber_security_db", alias="MONGODB_DB_NAME")
    mongodb_user_collection: str = Field("users", alias="MONGODB_USER_COLLECTION")

    gov_email_domain: str = Field("gov.in", alias="GOV_EMAIL_DOMAIN")
    frontend_origin: str = Field("http://localhost:5173", alias="FRONTEND_ORIGIN")

    initial_super_admin_name: str = Field("Bootstrap Admin", alias="INITIAL_SUPER_ADMIN_NAME")
    initial_super_admin_email: str = Field("", alias="INITIAL_SUPER_ADMIN_EMAIL")
    initial_super_admin_password: str = Field("", alias="INITIAL_SUPER_ADMIN_PASSWORD")

    token_cookie_name: str = "access_token"
    token_cookie_secure: bool = Field(False, alias="TOKEN_COOKIE_SECURE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
