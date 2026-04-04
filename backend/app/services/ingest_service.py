from datetime import datetime
from typing import Dict, Any, Optional
from app.schemas import EventIn
from app.repositories.event_repo import EventRepository
from app.repositories.alert_repo import AlertRepository


# Ingest service indexes events and raises alerts.
__all__ = ["IngestService", "process_event", "decision_engine", "evaluate_event"]


async def decision_engine(event: EventIn) -> Dict[str, Any]:
    print("---- DECISION ENGINE START ----")

    severity = evaluate_event(event)
    print("Incoming severity:", severity, type(severity))

    severity_normalized = severity.lower() if isinstance(severity, str) else severity
    print("Normalized severity:", severity_normalized)

    if severity_normalized in ["high", "medium"]:
        print("Condition PASSED → creating alert")

        try:
            alert_doc = {
                "event_id": event.event_id,
                "severity": severity_normalized,
                "status": "active"
            }

            print("Calling insert_alert...")

            repo = AlertRepository()
            alert_id = await repo.insert_alert(alert_doc)

            print("Returned alert_id:", alert_id)

            return {
                "alert_created": True if alert_id else False,
                "severity": severity_normalized,
                "alert_id": alert_id
            }

        except Exception as e:
            print("ALERT INSERT ERROR:", e)
            return {
                "alert_created": False,
                "severity": severity_normalized,
                "alert_id": None
            }

    else:
        print("Condition FAILED → no alert")

    return {
        "alert_created": False,
        "severity": severity_normalized,
        "alert_id": None
    }


def evaluate_event(event: EventIn) -> str:
    tl = event.ml.threat_level
    tl_normalized = tl.strip().lower() if isinstance(tl, str) else "low"

    if tl_normalized == "high":
        print("HIGH THREAT")
        return "high"
    if tl_normalized == "medium":
        print("MEDIUM THREAT")
        return "medium"

    print("LOW THREAT")
    return "low"


class IngestService:
    def __init__(self) -> None:
        self._event_repo = EventRepository()
        self._alert_repo = AlertRepository()

    async def ingest(self, event: EventIn) -> Dict[str, Any]:
        event_doc = event.dict(by_alias=True)
        try:
            event_id = await self._event_repo.index_event(event_doc)
        except Exception as exc:
            print("error indexing event:", exc)
            event_id = event.event_id

        decision = await decision_engine(event)
        alert_id = decision.get("alert_id")
        alert_created = decision.get("alert_created", False)
        severity = decision.get("severity")

        return {"event_id": event_id, "alert_id": alert_id, "alert_created": alert_created, "severity": severity}


async def process_event(event: EventIn) -> Dict[str, Any]:
    print("Processing event:", event.json())
    event_doc = event.dict(by_alias=True)
    try:
        repo = EventRepository()
        event_id = await repo.index_event(event_doc)
        print(f"Indexed event, event_id={event_id}")
    except Exception as exc:
        print("error indexing event:", exc)
        event_id = event.event_id

    # Call decision engine to evaluate event for alerting
    try:
        decision = await decision_engine(event)
    except Exception as exc:
        print("decision_engine error:", exc)
        decision = {"alert_created": False, "severity": "unknown", "alert_id": None}

    if decision is not None and decision.get("alert_created"):
        print("Alert created:", decision.get("alert_id"), "severity=", decision.get("severity"))

    return {
        "event_id": event_id,
        "alert_created": bool(decision.get("alert_created", False)),
        "severity": str(decision.get("severity", "low")),
        "alert_id": decision.get("alert_id"),
    }
