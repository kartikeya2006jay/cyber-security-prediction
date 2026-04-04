from typing import Any, Dict, Optional
from pydantic import BaseModel
from datetime import datetime


# Event and alert payload models.
class NetworkEndpoint(BaseModel):
    ip: str
    port: int


class EventML(BaseModel):
    attack_probability: float
    anomaly_score: float
    threat_level: str


class EventIn(BaseModel):
    event_id: str
    event_type: str
    timestamp: str
    source: NetworkEndpoint
    destination: NetworkEndpoint
    protocol: str
    metadata: Dict[str, Any]
    features: Dict[str, Any]
    ml: EventML


class Alert(BaseModel):
    event_id: str
    created_at: datetime
    alert_type: str
    details: Dict[str, Any]
    score: Optional[float]
