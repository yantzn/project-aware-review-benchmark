from __future__ import annotations


def build_audit_payload(*, user_id: int, access_token: str) -> dict[str, str | int]:
    masked = access_token[:4] + "***" if access_token else "***"
    return {
        "user_id": user_id,
        "access_token": masked,
    }
