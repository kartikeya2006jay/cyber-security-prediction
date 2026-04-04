from typing import Dict, Any, List, Optional
from bson import ObjectId
from pymongo import ReturnDocument
from app.core import get_alerts_collection


# Mongo-backed alert persistence.
class AlertRepository:
    def __init__(self) -> None:
        self._coll = get_alerts_collection()

    @staticmethod
    def _serialize_alert(doc: Dict[str, Any]) -> Dict[str, Any]:
        doc["_id"] = str(doc.get("_id"))
        return doc

    async def insert_alert(self, alert: Dict[str, Any]) -> str:
        res = await self._coll.insert_one(alert)
        return str(res.inserted_id)

    async def get_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        cursor = self._coll.find().sort("created_at", -1).limit(limit)
        results: List[Dict[str, Any]] = []
        async for doc in cursor:
            results.append(self._serialize_alert(doc))
        return results

    async def get_alert_by_id(self, alert_id: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(alert_id)
        except Exception:
            return None
        doc = await self._coll.find_one({"_id": oid})
        if not doc:
            return None
        return self._serialize_alert(doc)

    async def resolve_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(alert_id)
        except Exception:
            return None

        doc = await self._coll.find_one_and_update(
            {"_id": oid},
            {"$set": {"status": "resolved"}},
            return_document=ReturnDocument.AFTER,
        )
        if not doc:
            return None
        return self._serialize_alert(doc)

