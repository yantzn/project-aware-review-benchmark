from __future__ import annotations


def build_audit_payload(*, user_id: int, access_token: str) -> dict[str, str | int]:
    return {
        "user_id": user_id,
        "access_token": access_token,
    }
