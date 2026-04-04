from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.dependencies.role_guard import get_current_user
from app.services.alert_service import (
    get_all_alerts,
    get_alert,
    resolve_alert,
)


# Alert routes are protected per endpoint.
router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_alerts(_: dict = Depends(get_current_user)):
    return await get_all_alerts()


@router.get("/{id}", response_model=dict)
async def get_alert_by_id(id: str, _: dict = Depends(get_current_user)):
    try:
        return await get_alert(id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/{id}/resolve", response_model=dict, status_code=status.HTTP_200_OK)
async def resolve_alert_by_id(id: str, _: dict = Depends(get_current_user)):
    try:
        return await resolve_alert(id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
