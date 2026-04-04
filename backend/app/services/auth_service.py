import logging
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.core.config import get_settings
from app.core.database import get_users_collection
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user_model import UserRole, new_user_document
from app.schemas.auth import CreateUserRequest, LoginRequest
from app.services.security_event_service import emit_auth_event


# Auth business logic lives here.
security_logger = logging.getLogger("security.auth")


def _serialize_user(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(document["_id"]),
        "username": document.get("username") or document.get("name", ""),
        "email": document["email"],
        "role": document["role"],
        "created_at": document["created_at"],
        "last_login": document.get("last_login"),
    }


def _is_gov_email(email: str) -> bool:
    settings = get_settings()
    return email.lower().endswith(f"@{settings.gov_email_domain.lower()}")


async def create_user(payload: CreateUserRequest) -> dict[str, Any]:
    payload_data = payload.model_dump()
    email = str(payload_data["email"]).strip().lower()

    if not _is_gov_email(email):
        raise ValueError("Only government domain emails are allowed")

    collection = get_users_collection()
    security_logger.debug("auth.db.selected collection=users")

    role = payload_data["role"]
    role_value = role.value if isinstance(role, UserRole) else str(role)
    role_enum = UserRole(role_value)

    user_doc = new_user_document(
        username=str(payload_data["username"]).strip(),
        email=email,
        hashed_password=hash_password(str(payload_data["password"])),
        role=role_enum,
    )

    security_logger.debug(
        "user.create.attempt email=%s role=%s",
        email,
        role_value,
    )

    # Prevent duplicate registration before insert.
    existing_user = await collection.find_one({"email": email}, {"_id": 1})
    if existing_user is not None:
        raise ValueError("User with this email already exists")

    try:
        insert_result = await collection.insert_one(user_doc)
    except DuplicateKeyError as exc:
        raise ValueError("User with this email already exists") from exc

    created_doc = await collection.find_one({"_id": insert_result.inserted_id})
    if not created_doc:
        raise RuntimeError("Unable to fetch created user")

    security_logger.info(
        "user.created email=%s role=%s",
        created_doc["email"],
        created_doc["role"],
    )
    await emit_auth_event(
        "user_created",
        {"email": created_doc["email"], "role": created_doc["role"]},
    )
    return _serialize_user(created_doc)


async def authenticate_user(
    payload: LoginRequest,
    client_ip: str,
    user_agent: str,
) -> tuple[dict[str, Any], str, int]:
    collection = get_users_collection()
    security_logger.debug("auth.db.selected collection=users")

    email = payload.email.lower()
    user_doc = await collection.find_one({"email": email})
    if not user_doc or not verify_password(payload.password, user_doc["hashed_password"]):
        security_logger.warning(
            "auth.login.failed email=%s ip=%s ua=%s",
            email,
            client_ip,
            user_agent,
        )
        raise ValueError("Invalid credentials")

    now = datetime.now(timezone.utc)
    await collection.update_one(
        {"_id": user_doc["_id"]},
        {"$set": {"last_login": now}},
    )

    settings = get_settings()
    token_exp_minutes = settings.access_token_expire_minutes
    token = create_access_token(
        {
            "sub": str(user_doc["_id"]),
            "email": user_doc["email"],
            "role": user_doc["role"],
            "username": user_doc.get("username") or user_doc.get("name", ""),
        },
        expires_minutes=token_exp_minutes,
    )

    security_logger.info(
        "auth.login.success email=%s role=%s ip=%s ua=%s",
        email,
        user_doc["role"],
        client_ip,
        user_agent,
    )
    await emit_auth_event(
        "login_success",
        {"email": email, "role": user_doc["role"], "ip": client_ip},
    )

    user_doc["last_login"] = now
    return _serialize_user(user_doc), token, token_exp_minutes * 60


async def get_user_by_id(user_id: str) -> dict[str, Any] | None:
    collection = get_users_collection()

    if not ObjectId.is_valid(user_id):
        return None

    user_doc = await collection.find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        return None
    return _serialize_user(user_doc)


async def list_users() -> list[dict[str, Any]]:
    collection = get_users_collection()

    users: list[dict[str, Any]] = []
    async for doc in collection.find({}, {"hashed_password": 0}).sort("created_at", -1):
        users.append(_serialize_user(doc))
    return users


async def update_user_role(user_id: str, role: UserRole) -> dict[str, Any]:
    collection = get_users_collection()

    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user id")

    object_id = ObjectId(user_id)
    current_user = await collection.find_one({"_id": object_id})
    if not current_user:
        raise ValueError("User not found")

    if (
        current_user["role"] == UserRole.SUPER_ADMIN.value
        and role != UserRole.SUPER_ADMIN
    ):
        super_admin_count = await collection.count_documents(
            {"role": UserRole.SUPER_ADMIN.value}
        )
        if super_admin_count <= 1:
            raise ValueError("Cannot demote the last SUPER_ADMIN")

    update_result = await collection.update_one(
        {"_id": object_id},
        {"$set": {"role": role.value}},
    )
    if update_result.matched_count == 0:
        raise ValueError("User not found")

    updated_user = await collection.find_one({"_id": object_id})
    if not updated_user:
        raise RuntimeError("Unable to fetch updated user")

    security_logger.warning(
        "user.role.updated email=%s role=%s",
        updated_user["email"],
        updated_user["role"],
    )
    await emit_auth_event(
        "user_role_updated",
        {"email": updated_user["email"], "role": updated_user["role"]},
    )
    return _serialize_user(updated_user)


async def delete_user(user_id: str) -> None:
    collection = get_users_collection()

    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user id")

    object_id = ObjectId(user_id)
    user = await collection.find_one({"_id": object_id})
    if not user:
        raise ValueError("User not found")

    if user["role"] == UserRole.SUPER_ADMIN.value:
        super_admin_count = await collection.count_documents(
            {"role": UserRole.SUPER_ADMIN.value}
        )
        if super_admin_count <= 1:
            raise ValueError("Cannot delete the last SUPER_ADMIN")

    await collection.delete_one({"_id": object_id})
    security_logger.warning("user.deleted email=%s", user["email"])
    await emit_auth_event("user_deleted", {"email": user["email"]})


async def bootstrap_initial_super_admin() -> None:
    settings = get_settings()
    email = settings.initial_super_admin_email.strip().lower()
    password = settings.initial_super_admin_password

    if not email or not password:
        return

    collection = get_users_collection()
    existing = await collection.find_one({"email": email})
    if existing:
        if existing.get("role") != UserRole.SUPER_ADMIN.value:
            await collection.update_one(
                {"_id": existing["_id"]},
                {"$set": {"role": UserRole.SUPER_ADMIN.value}},
            )
            security_logger.warning(
                "bootstrap.super_admin.role_restored email=%s old_role=%s",
                email,
                existing.get("role"),
            )
            await emit_auth_event(
                "bootstrap_super_admin_role_restored",
                {"email": email, "old_role": existing.get("role")},
            )
        return

    bootstrap_request = CreateUserRequest(
        username=settings.initial_super_admin_name,
        email=email,
        password=password,
        role=UserRole.SUPER_ADMIN,
    )
    await create_user(bootstrap_request)
    security_logger.warning("bootstrap.super_admin.created email=%s", email)
