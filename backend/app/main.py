from fastapi import FastAPI
from fastapi.responses import ORJSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .logging_config import configure_logging
from .routers import health, ingest, search, ask, admin, auth


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="SRM UniChat API", default_response_class=ORJSONResponse)

    @app.get("/")
    def root():
        """Redirect root to API documentation."""
        return RedirectResponse(url="/docs")

    # CORS
    # Parse CORS origins from comma-separated string. If none provided,
    # allow any origin WITHOUT credentials to satisfy browser preflight.
    cors_origins = []
    if settings.cors_allow_origins:
        cors_origins = [origin.strip() for origin in settings.cors_allow_origins.split(',') if origin.strip()]

    allow_any_origin = len(cors_origins) == 0

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins if not allow_any_origin else ["*"],
        allow_credentials=False if allow_any_origin else True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api")
    app.include_router(auth.router, prefix="/api/auth")
    app.include_router(ingest.router, prefix="/api")
    app.include_router(search.router, prefix="/api")
    app.include_router(ask.router, prefix="/api")
    app.include_router(admin.router, prefix="/api")
    return app


app = create_app()


