from __future__ import annotations

from typing import Any

from .exceptions import DuplicateEmailError, ValidationError
from .user_service import UserService


def create_user(service: UserService, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    try:
        user = service.register_user(
            email=str(payload.get("email", "")),
            name=str(payload.get("name", "")),
            age=int(payload.get("age", 0)),
        )
    except DuplicateEmailError:
        return 409, {"error": "DUPLICATE_EMAIL"}
    except (ValidationError, ValueError, TypeError):
        return 400, {"error": "VALIDATION_ERROR"}

    return 201, {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "age": user.age,
    }
