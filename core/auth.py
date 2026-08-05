from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any, Optional

from fastapi import Header, HTTPException, status


class CurrentUser:
    def __init__(self, username: str, roles: list[str]):
        self.username = username
        self.roles = roles


class _AuthRecord(CurrentUser):
    def __init__(self, username: str, password: str, roles: list[str]):
        super().__init__(username, roles)
        self.password = password


def load_auth_users() -> list[_AuthRecord]:
    users_json = os.getenv("AUTH_USERS_JSON")
    if users_json:
        try:
            parsed = json.loads(users_json)
            return [
                _AuthRecord(
                    username=item["username"],
                    password=item["password"],
                    roles=list(item.get("roles", [])),
                )
                for item in parsed
            ]
        except (KeyError, TypeError, json.JSONDecodeError):
            return []

    username = os.getenv("AUTH_USERNAME")
    password = os.getenv("AUTH_PASSWORD")
    roles = [role.strip() for role in os.getenv("AUTH_ROLES", "admin").split(",") if role.strip()]
    if username and password:
        return [_AuthRecord(username=username, password=password, roles=roles or ["admin"])]
    return []


def authenticate_user(username: str, password: str, users: list[_AuthRecord]) -> Optional[CurrentUser]:
    for user in users:
        if user.username == username and user.password == password:
            return CurrentUser(user.username, user.roles)
    return None


def _auth_secret() -> str:
    return os.getenv("JWT_SECRET_KEY", "development-secret-change-me")


def _encode_token(payload: dict[str, Any]) -> str:
    raw_payload = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    encoded_payload = base64.urlsafe_b64encode(raw_payload).decode("ascii").rstrip("=")
    signature = hmac.new(_auth_secret().encode("utf-8"), encoded_payload.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{encoded_payload}.{signature}"


def _decode_token(token: str) -> Optional[CurrentUser]:
    try:
        encoded_payload, signature = token.split(".", 1)
    except ValueError:
        return None

    expected_signature = hmac.new(
        _auth_secret().encode("utf-8"),
        encoded_payload.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        return None

    padded_payload = encoded_payload + "=" * (-len(encoded_payload) % 4)
    try:
        payload = json.loads(base64.urlsafe_b64decode(padded_payload.encode("ascii")))
    except (ValueError, json.JSONDecodeError):
        return None

    expires_at = int(payload.get("exp", 0))
    if expires_at <= int(time.time()):
        return None

    username = payload.get("sub")
    roles = payload.get("roles", [])
    if not isinstance(username, str) or not isinstance(roles, list):
        return None
    return CurrentUser(username=username, roles=[str(role) for role in roles])


def create_access_token(username: str, roles: list[str]) -> tuple[str, int]:
    expires_at = int(time.time()) + int(os.getenv("JWT_EXPIRE_MINUTES", "120")) * 60
    token = _encode_token({"sub": username, "roles": roles, "exp": expires_at})
    return token, expires_at


def require_roles(*allowed_roles: str):
    async def dependency(authorization: Optional[str] = Header(default=None)) -> CurrentUser:
        if authorization is None or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

        user = _decode_token(authorization.removeprefix("Bearer ").strip())
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
        if allowed_roles and not any(role in user.roles for role in allowed_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user

    return dependency
