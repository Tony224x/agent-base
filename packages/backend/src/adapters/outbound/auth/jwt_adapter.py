from __future__ import annotations

import jwt

from src.core.domain.value_objects.user_context import UserContext


class JWTAuthAdapter:
    """JWT-based authentication adapter."""

    def __init__(self, secret: str, algorithm: str = "HS256") -> None:
        self._secret = secret
        self._algorithm = algorithm

    async def validate_token(self, token: str) -> UserContext | None:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except jwt.InvalidTokenError:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        return UserContext(
            user_id=user_id,
            tenant_id=payload.get("tenant_id"),
            roles=payload.get("roles", []),
            metadata={k: v for k, v in payload.items() if k not in ("sub", "tenant_id", "roles", "exp", "iat")},
        )
