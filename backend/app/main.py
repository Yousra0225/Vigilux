"""Vigilux Backend - Main Application Entry Point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.v1 import auth as auth_router
from app.api.v1 import competitors
from app.api.v1 import projects
from app.api.v1 import radar
from app.api.v1 import dashboard
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}...")
    yield
    # Shutdown
    print(f"Shutting down {settings.PROJECT_NAME}...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, tags=["Health"])
app.include_router(auth_router.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Auth"])
app.include_router(competitors.router, prefix=f"{settings.API_V1_PREFIX}/competitors", tags=["Competitors"])
app.include_router(projects.router, prefix=f"{settings.API_V1_PREFIX}/projects", tags=["Projects"])
app.include_router(radar.router, prefix=f"{settings.API_V1_PREFIX}/radar", tags=["Radar"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_PREFIX}/dashboard", tags=["Dashboard"])


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint.

    Returns:
        A welcome message with API information.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
    }
