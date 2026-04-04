from typing import Any, Dict, List

from app.repositories.alert_repo import AlertRepository

__all__ = ["AlertService", "get_all_alerts", "get_alert", "resolve_alert"]


# Alert service wraps repository access.
class AlertService:
    def __init__(self) -> None:
        self._repo = AlertRepository()

    async def get_all_alerts(self) -> List[Dict[str, Any]]:
        return await self._repo.get_alerts()

    async def get_alert(self, alert_id: str) -> Dict[str, Any]:
        alert = await self._repo.get_alert_by_id(alert_id)
        if alert is None:
            raise ValueError("Alert not found")
        return alert

    async def resolve_alert(self, alert_id: str) -> Dict[str, Any]:
        alert = await self._repo.resolve_alert(alert_id)
        if alert is None:
            raise ValueError("Alert not found")
        return alert


async def get_all_alerts() -> List[Dict[str, Any]]:
    service = AlertService()
    return await service.get_all_alerts()


async def get_alert(alert_id: str) -> Dict[str, Any]:
    service = AlertService()
    return await service.get_alert(alert_id)


async def resolve_alert(alert_id: str) -> Dict[str, Any]:
    service = AlertService()
    return await service.resolve_alert(alert_id)
