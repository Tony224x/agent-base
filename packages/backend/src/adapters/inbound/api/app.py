from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.adapters.inbound.api.dependencies import get_auth_adapter
from src.adapters.inbound.api.middleware.auth_middleware import AuthMiddleware
from src.adapters.inbound.api.routes import health, conversations, chat, extraction


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Agent Base",
        description="AI Agent backend with LangGraph",
        version="0.1.0",
    )

    # CORS -- permissive for development, restrict in production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Auth middleware
    app.add_middleware(AuthMiddleware, auth_adapter=get_auth_adapter())

    # Routes
    app.include_router(health.router)
    app.include_router(conversations.router)
    app.include_router(chat.router)
    app.include_router(extraction.router)

    return app
