from pydantic import Field

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


# Central backend settings.
class Settings(BaseSettings):
    app_name: str = "cyber-backend"

    # Shared Mongo connection for both alerts and auth data.
    MONGO_URI: str = Field(..., env="MONGO_URI")
    ALERTS_DB_NAME: str = Field("alerts_db", env="ALERTS_DB_NAME")
    AUTH_DB_NAME: str = Field("auth_db", env="AUTH_DB_NAME")
    MONGODB_USER_COLLECTION: str = Field("users", env="MONGODB_USER_COLLECTION")

    # Elasticsearch settings stay separate from Mongo settings.
    es_hosts: str = Field(..., env="ES_HOSTS")
    es_index: str = Field(..., env="ES_INDEX")
    alert_threshold: float = Field(0.8, env="ALERT_THRESHOLD")

    # Auth token settings.
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    token_cookie_name: str = Field("access_token", env="TOKEN_COOKIE_NAME")
    token_cookie_secure: bool = Field(False, env="TOKEN_COOKIE_SECURE")

    # Government email and bootstrap admin values.
    gov_email_domain: str = Field("gov.in", env="GOV_EMAIL_DOMAIN")
    frontend_origin: str = Field("http://localhost:3000", env="FRONTEND_ORIGIN")

    initial_super_admin_name: str = Field("System Admin", env="INITIAL_SUPER_ADMIN_NAME")
    initial_super_admin_email: str = Field("", env="INITIAL_SUPER_ADMIN_EMAIL")
    initial_super_admin_password: str = Field("", env="INITIAL_SUPER_ADMIN_PASSWORD")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()


def get_settings() -> Settings:
    return settings
