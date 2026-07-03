import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

ALLOWED_ROLES = {"viewer", "chef", "admin"}

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "120"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class CurrentUser(BaseModel):
    username: str
    roles: list[str]


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("utf-8")


def _b64url_decode(raw: str) -> bytes:
    padding = "=" * (-len(raw) % 4)
    return base64.urlsafe_b64decode(raw + padding)


def _jwt_sign(data: bytes) -> str:
    digest = hmac.new(JWT_SECRET_KEY.encode("utf-8"), data, hashlib.sha256).digest()
    return _b64url_encode(digest)


def create_access_token(username: str, roles: list[str]) -> tuple[str, int]:
    expires_at = int(time.time()) + (JWT_EXPIRE_MINUTES * 60)
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": username,
        "roles": roles,
        "exp": expires_at,
    }
    header_part = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_part = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_part}.{payload_part}".encode("utf-8")
    signature = _jwt_sign(signing_input)
    return f"{header_part}.{payload_part}.{signature}", expires_at


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        header_part, payload_part, signature_part = token.split(".")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format") from exc

    signing_input = f"{header_part}.{payload_part}".encode("utf-8")
    expected_sig = _jwt_sign(signing_input)
    if not secrets.compare_digest(signature_part, expected_sig):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token signature")

    try:
        payload = json.loads(_b64url_decode(payload_part).decode("utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload") from exc

    exp = int(payload.get("exp", 0))
    if exp <= int(time.time()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")

    return payload


def _pbkdf2_hash(password: str, salt: str, iterations: int = 390000) -> str:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    return base64.b64encode(digest).decode("utf-8")


def hash_password(password: str) -> str:
    iterations = 390000
    salt = secrets.token_hex(16)
    digest = _pbkdf2_hash(password, salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt}${digest}"


def verify_password(plain_password: str, stored_value: str) -> bool:
    if stored_value.startswith("pbkdf2_sha256$"):
        try:
            _, iterations_raw, salt, digest = stored_value.split("$", 3)
            iterations = int(iterations_raw)
            computed = _pbkdf2_hash(plain_password, salt, iterations)
            return secrets.compare_digest(computed, digest)
        except Exception:
            return False

    # Backward-compatible plain-text fallback for bootstrapping.
    return secrets.compare_digest(plain_password, stored_value)


def load_auth_users() -> dict[str, dict[str, Any]]:
    raw = os.getenv("AUTH_USERS_JSON", "").strip()
    if raw:
        try:
            parsed = json.loads(raw)
        except Exception as exc:
            raise RuntimeError("AUTH_USERS_JSON is not valid JSON") from exc

        users: dict[str, dict[str, Any]] = {}
        for item in parsed:
            username = str(item.get("username", "")).strip()
            if not username:
                continue
            roles = [r for r in item.get("roles", ["viewer"]) if r in ALLOWED_ROLES]
            if not roles:
                roles = ["viewer"]
            password_hash = str(item.get("password_hash", "")).strip()
            password = str(item.get("password", "")).strip()
            if not password_hash and password:
                password_hash = hash_password(password)
            if not password_hash:
                continue
            users[username] = {"password_hash": password_hash, "roles": roles}
        if users:
            return users

    username = os.getenv("AUTH_USERNAME", "admin")
    password = os.getenv("AUTH_PASSWORD", "change-me")
    roles = [r.strip() for r in os.getenv("AUTH_ROLES", "admin").split(",") if r.strip() in ALLOWED_ROLES]
    if not roles:
        roles = ["admin"]
    return {username: {"password_hash": hash_password(password), "roles": roles}}


def authenticate_user(username: str, password: str, users: dict[str, dict[str, Any]]) -> CurrentUser | None:
    account = users.get(username)
    if not account:
        return None

    if not verify_password(password, str(account.get("password_hash", ""))):
        return None

    roles = [r for r in account.get("roles", []) if r in ALLOWED_ROLES]
    if not roles:
        roles = ["viewer"]
    return CurrentUser(username=username, roles=roles)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    payload = decode_access_token(token)
    username = str(payload.get("sub", "")).strip()
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    roles = payload.get("roles", [])
    if not isinstance(roles, list):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token roles")
    normalized_roles = [str(r) for r in roles if str(r) in ALLOWED_ROLES]
    if not normalized_roles:
        normalized_roles = ["viewer"]
    return CurrentUser(username=username, roles=normalized_roles)


def require_roles(*allowed_roles: str):
    allowed_set = {r for r in allowed_roles if r in ALLOWED_ROLES}

    async def checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not any(role in allowed_set for role in user.roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return checker