from fastapi import FastAPI

from app.api.routes import router
from app.core_config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(router, prefix="/api")


@app.get("/")
def root() -> dict:
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/health",
        "analyze": "/api/copilot/analyze",
    }
