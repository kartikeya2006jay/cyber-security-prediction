import logging
from typing import Any


# Security event logging stub.
security_event_logger = logging.getLogger("security.events")


async def emit_auth_event(event_type: str, payload: dict[str, Any]) -> None:
    security_event_logger.info("auth.event type=%s payload=%s", event_type, payload)
