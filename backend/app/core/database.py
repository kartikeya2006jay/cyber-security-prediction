import logging

from elasticsearch import AsyncElasticsearch
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Any

from app.core.config import settings


# Shared clients for MongoDB and Elasticsearch.
logger = logging.getLogger("app.database")


class ES:
    client: AsyncElasticsearch | None = None


class Mongo:
    client: AsyncIOMotorClient | None = None
    alerts_db: Any | None = None
    auth_db: Any | None = None


async def connect_es() -> None:
    if ES.client is None:
        hosts = [h.strip() for h in settings.es_hosts.split(",")]
        ES.client = AsyncElasticsearch(hosts)


async def close_es() -> None:
    if ES.client is not None:
        await ES.client.close()
        ES.client = None


def get_es_client() -> AsyncElasticsearch:
    if ES.client is None:
        raise RuntimeError("Elasticsearch client not initialized")
    return ES.client


async def connect_mongo() -> None:
    if Mongo.client is None:
        Mongo.client = AsyncIOMotorClient(settings.MONGO_URI)
        # One client, two logical databases.
        Mongo.alerts_db = Mongo.client[settings.ALERTS_DB_NAME]
        Mongo.auth_db = Mongo.client[settings.AUTH_DB_NAME]
        logger.info(
            "mongo.db.selected alerts_db=%s auth_db=%s",
            settings.ALERTS_DB_NAME,
            settings.AUTH_DB_NAME,
        )


async def close_mongo() -> None:
    if Mongo.client is not None:
        Mongo.client.close()
        Mongo.client = None
        Mongo.alerts_db = None
        Mongo.auth_db = None


def get_alerts_collection() -> Any:
    if Mongo.alerts_db is None:
        raise RuntimeError("Mongo client not initialized")
    # Alerts always live in the alerts database.
    return Mongo.alerts_db["alerts"]


def get_users_collection() -> Any:
    if Mongo.auth_db is None:
        raise RuntimeError("Mongo client not initialized")
    # Auth users are stored in the auth database only.
    return Mongo.auth_db[settings.MONGODB_USER_COLLECTION]
