from fastapi import FastAPI

from adapters.inbound.api.routers import health_router


def create_web_api() -> FastAPI:
    """Create and configure the FastAPI web application."""
    app = FastAPI(
        title="Review Genie API",
        description="A web API for Review Genie application",
        version="0.1.0",
    )

    # Include routers
    app.include_router(health_router, prefix="/api/v1")

    return app


def bootstrap_web_api() -> FastAPI:
    """Bootstrap the web application.

    This factory method creates and configures the FastAPI application
    with all necessary components.

    Returns:
        FastAPI: Configured FastAPI application instance.
    """
    # Create the web API adapter
    app = create_web_api()

    # Add any additional configuration here
    # For example: middleware, exception handlers, startup/shutdown events

    return app
