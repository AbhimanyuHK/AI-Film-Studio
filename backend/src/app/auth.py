from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException, status

from app.config import settings


@dataclass(frozen=True)
class Principal:
    subject: str
    client_id: str | None = None
    role: str = "client_user"


def _jwt_principal(authorization: str | None) -> Principal:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    token = authorization[7:].strip()
    if not settings.jwt_secret:
        raise HTTPException(status_code=500, detail="JWT authentication is not configured")
    try:
        options = {"require": ["sub", "exp"]}
        kwargs = {"algorithms": [settings.jwt_algorithm], "options": options}
        if settings.jwt_issuer:
            kwargs["issuer"] = settings.jwt_issuer
        if settings.jwt_audience:
            kwargs["audience"] = settings.jwt_audience
        claims = jwt.decode(token, settings.jwt_secret, **kwargs)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token") from exc

    role = str(claims.get("role", "client_user"))
    if role not in {"platform_admin", "client_admin", "client_user"}:
        raise HTTPException(status_code=403, detail="Invalid role")
    client_id = claims.get("client_id")
    if role != "platform_admin" and not client_id:
        raise HTTPException(status_code=403, detail="Client scope is required")
    return Principal(subject=str(claims["sub"]), client_id=str(client_id) if client_id else None, role=role)


def get_principal(
    authorization: Annotated[str | None, Header()] = None,
    x_actor_id: Annotated[str | None, Header()] = None,
) -> Principal:
    """Authenticate the request using JWT in production and explicit identity in development."""
    if settings.auth_mode == "development":
        if not x_actor_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
        return Principal(subject=x_actor_id, role="platform_admin")
    return _jwt_principal(authorization)


def require_platform_admin(principal: Annotated[Principal, Depends(get_principal)]) -> Principal:
    if principal.role != "platform_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
    return principal
