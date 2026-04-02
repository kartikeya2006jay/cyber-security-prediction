import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import get_settings
from app.core.database import close_mongo_connection, connect_to_mongo
from app.core.rate_limiter import limiter
from app.routes.auth_routes import router as auth_router
from app.routes.protected_routes import router as protected_router
from app.services.auth_service import bootstrap_initial_super_admin


@asynccontextmanager
async def lifespan(_: FastAPI):
    await connect_to_mongo()
    await bootstrap_initial_super_admin()
    yield
    await close_mongo_connection()


settings = get_settings()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(protected_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
