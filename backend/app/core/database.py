from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings

_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None


def get_db() -> AsyncIOMotorDatabase:
    if _database is None:
        raise RuntimeError("Database is not initialized")
    return _database


def get_user_collection_name() -> str:
    settings = get_settings()
    return settings.mongodb_user_collection


async def connect_to_mongo() -> None:
    global _client, _database
    settings = get_settings()
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    _database = _client[settings.mongodb_db_name]
    await _database[get_user_collection_name()].create_index("email", unique=True)


async def close_mongo_connection() -> None:
    global _client, _database
    if _client is not None:
        _client.close()
    _client = None
    _database = None
