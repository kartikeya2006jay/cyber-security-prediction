from typing import Dict, Any, List
from elasticsearch import exceptions as es_exceptions
from app.core import get_es_client, settings


# Elasticsearch-backed event persistence.
class EventRepository:
    def __init__(self) -> None:
        self._client = get_es_client()
        self._index = settings.es_index

    async def _ensure_index(self) -> None:
        try:
            exists = await self._client.indices.exists(index=self._index)
        except Exception:
            return

        if not exists:
            mapping = {
                "mappings": {
                    "properties": {
                        "timestamp": {"type": "date"},
                        "event_id": {"type": "keyword"},
                        "event_type": {"type": "keyword"},
                        "protocol": {"type": "keyword"},
                        "source": {
                            "properties": {
                                "ip": {"type": "ip"},
                                "port": {"type": "integer"},
                            }
                        },
                        "destination": {
                            "properties": {
                                "ip": {"type": "ip"},
                                "port": {"type": "integer"},
                            }
                        },
                        "metadata": {"type": "object", "enabled": False},
                        "features": {"type": "object", "enabled": False},
                        "ml": {
                            "properties": {
                                "attack_probability": {"type": "float"},
                                "anomaly_score": {"type": "float"},
                                "threat_level": {"type": "keyword"},
                            }
                        },
                    }
                }
            }
            try:
                await self._client.indices.create(index=self._index, body=mapping)
            except Exception:
                return

    async def index_event(self, event: Dict[str, Any]) -> str:
        fallback_event_id = str(event.get("event_id") or "unknown-event-id")
        try:
            await self._ensure_index()
            resp = await self._client.index(index=self._index, document=event)
            print("ES response:", resp)
            event_id = resp.get("_id")
            if event_id:
                return str(event_id)
            print("Elasticsearch indexing error: missing _id in response")
            return fallback_event_id
        except es_exceptions.ConnectionError as exc:
            print("Elasticsearch connection error:", exc)
            return fallback_event_id
        except Exception as exc:
            print("Elasticsearch indexing error:", exc)
            return fallback_event_id

    async def search_events(self, query: Dict[str, Any], size: int = 10) -> List[Dict[str, Any]]:
        try:
            await self._ensure_index()
            resp = await self._client.search(index=self._index, query=query, size=size)
            hits = resp.get("hits", {}).get("hits", [])
            results: List[Dict[str, Any]] = []
            for h in hits:
                src = h.get("_source", {})
                src["event_id"] = h.get("_id")
                results.append(src)
            return results
        except es_exceptions.ConnectionError as exc:
            print("Elasticsearch connection error:", exc)
            return []
        except Exception as exc:
            print("Elasticsearch search error:", exc)
            return []

