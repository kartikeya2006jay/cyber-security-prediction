import logging

logger = logging.getLogger("security.event")


async def emit_auth_event(event_type: str, payload: dict) -> None:
    # Pipeline integration hook: this is where Kafka producer logic can be added.
    logger.info("security.event type=%s payload=%s", event_type, payload)
