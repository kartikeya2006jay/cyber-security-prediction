from fastapi import APIRouter, Depends

from app.dependencies.role_guard import role_required
from app.models.user_model import UserRole

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview")
async def dashboard_overview(
    current_user: dict = Depends(
        role_required(
            UserRole.SUPER_ADMIN,
            UserRole.SECURITY_ANALYST,
            UserRole.INCIDENT_RESPONDER,
            UserRole.AUDITOR,
        )
    ),
) -> dict:
    return {
        "message": "Authenticated dashboard access granted",
        "role": current_user["role"],
    }


@router.get("/admin/panel")
async def admin_panel(
    _: dict = Depends(role_required(UserRole.SUPER_ADMIN)),
) -> dict:
    return {"message": "SUPER_ADMIN control panel"}


@router.get("/analyst/threats")
async def analyst_panel(
    _: dict = Depends(
        role_required(UserRole.SUPER_ADMIN, UserRole.SECURITY_ANALYST)
    ),
) -> dict:
    return {"message": "Threat monitoring stream"}


@router.post("/responder/actions")
async def responder_actions(
    _: dict = Depends(
        role_required(UserRole.SUPER_ADMIN, UserRole.INCIDENT_RESPONDER)
    ),
) -> dict:
    return {"message": "Incident response action accepted"}


@router.get("/auditor/reports")
async def auditor_reports(
    _: dict = Depends(role_required(UserRole.SUPER_ADMIN, UserRole.AUDITOR)),
) -> dict:
    return {"message": "Read-only audit reports"}
