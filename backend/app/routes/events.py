from fastapi import APIRouter, HTTPException, status
from app.schemas import EventIn
from app.services.ingest_service import process_event


# Event ingestion stays separate from auth.
router = APIRouter(prefix="/events", tags=["events"])


@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_event(event: EventIn):
    try:
        result = await process_event(event)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return result
