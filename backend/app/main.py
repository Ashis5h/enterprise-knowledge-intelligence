from time import perf_counter

from fastapi import Depends
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import get_current_user
from app.api.routes import analytics, auth, chat, documents, fine_tuning, health
from app.core.config import settings
from app.db.session import init_db
from app.services.agents.graph import warm_agent_workflow


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    protected = [Depends(get_current_user)]
    app.include_router(health.router, prefix="/api")
    app.include_router(auth.router, prefix="/api")
    app.include_router(chat.router, prefix="/api", dependencies=protected)
    app.include_router(documents.router, prefix="/api", dependencies=protected)
    app.include_router(analytics.router, prefix="/api", dependencies=protected)
    app.include_router(fine_tuning.router, prefix="/api", dependencies=protected)

    @app.on_event("startup")
    def prewarm_agents() -> None:
        init_db()
        warm_agent_workflow()

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        started_at = perf_counter()
        response = await call_next(request)
        elapsed_ms = (perf_counter() - started_at) * 1000
        response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.2f}"
        return response

    return app


app = create_app()
