from fastapi import FastAPI
from app.core import close_es, close_mongo, connect_es, connect_mongo
from app.routes import alerts, auth, events
from app.services.auth_service import bootstrap_initial_super_admin


# FastAPI application entry point.
app = FastAPI(title="Cyber Security Backend")

app.include_router(events.router)
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(auth.router)


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event() -> None:
    await connect_mongo()
    await bootstrap_initial_super_admin()
    await connect_es()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await close_es()
    await close_mongo()
