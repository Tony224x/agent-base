from __future__ import annotations

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware that validates JWT tokens and sets request.state.user."""

    EXCLUDED_PATHS = {"/api/health", "/docs", "/openapi.json", "/redoc"}

    def __init__(self, app, auth_adapter) -> None:
        super().__init__(app)
        self._auth = auth_adapter

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

        token = auth_header.removeprefix("Bearer ").strip()
        user_context = await self._auth.validate_token(token)

        if not user_context:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        request.state.user = user_context
        return await call_next(request)
