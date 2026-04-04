from datetime import datetime, timezone
from enum import Enum
from typing import Any


# User roles and user document helper.
class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    SECURITY_ANALYST = "SECURITY_ANALYST"
    INCIDENT_RESPONDER = "INCIDENT_RESPONDER"
    AUDITOR = "AUDITOR"


def new_user_document(
    *,
    username: str,
    email: str,
    hashed_password: str,
    role: UserRole,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    return {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "role": role.value,
        "created_at": now,
        "last_login": None,
    }
