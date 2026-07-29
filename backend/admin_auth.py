import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError


ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
ADMIN_JWT_SECRET = os.getenv("ADMIN_JWT_SECRET", "")
ADMIN_TOKEN_MINUTES = int(os.getenv("ADMIN_TOKEN_MINUTES", "60"))

security = HTTPBearer(auto_error=False)


def validate_admin_configuration() -> None:
    missing = []

    if not ADMIN_USERNAME:
        missing.append("ADMIN_USERNAME")

    if not ADMIN_PASSWORD:
        missing.append("ADMIN_PASSWORD")

    if not ADMIN_JWT_SECRET:
        missing.append("ADMIN_JWT_SECRET")

    if missing:
        raise RuntimeError(
            "Missing admin authentication environment variables: "
            + ", ".join(missing)
        )


def authenticate_admin(username: str, password: str) -> bool:
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        return False

    username_matches = secrets.compare_digest(
        username.strip(),
        ADMIN_USERNAME,
    )
    password_matches = secrets.compare_digest(
        password,
        ADMIN_PASSWORD,
    )

    return username_matches and password_matches


def create_admin_token(username: str) -> tuple[str, datetime]:
    if not ADMIN_JWT_SECRET:
        raise RuntimeError(
            "ADMIN_JWT_SECRET is not configured."
        )

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ADMIN_TOKEN_MINUTES
    )

    payload = {
        "sub": username,
        "role": "admin",
        "iat": datetime.now(timezone.utc),
        "exp": expires_at,
    }

    token = jwt.encode(
        payload,
        ADMIN_JWT_SECRET,
        algorithm="HS256",
    )

    return token, expires_at


def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            ADMIN_JWT_SECRET,
            algorithms=["HS256"],
        )
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired admin token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin role required.",
        )

    return payload
