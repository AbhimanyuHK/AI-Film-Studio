from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status


@dataclass(frozen=True)
class Principal:
    subject: str
    client_id: str | None = None
    role: str = "platform_admin"


def get_principal(x_actor_id: Annotated[str | None, Header()] = None) -> Principal:
    """Temporary development identity boundary.

    Production authentication must replace this dependency with an OIDC/JWT
    verifier. The actor ID is deliberately explicit so API authorization can be
    tested before an identity provider is integrated.
    """
    if not x_actor_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return Principal(subject=x_actor_id)


def require_platform_admin(principal: Annotated[Principal, Depends(get_principal)]) -> Principal:
    if principal.role != "platform_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
    return principal
