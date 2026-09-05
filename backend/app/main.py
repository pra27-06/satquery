"""
main.py
-------
FastAPI application entry point for SatQuery AI.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import settings
from .api.analyze import router as analyze_router
from .api.demos import router as demos_router
from .api.report import router as report_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Agentic Vision-Language Assistant for Remote Sensing Image Analysis (SIH26167)"
)

# CORS Configuration (Vite dev server + production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(analyze_router, prefix="/api", tags=["Analysis"])
app.include_router(demos_router, prefix="/api", tags=["SIH Demos"])
app.include_router(report_router, prefix="/api", tags=["Reports"])

# Static file serving for samples
if settings.SAMPLES_DIR.exists():
    app.mount("/samples", StaticFiles(directory=str(settings.SAMPLES_DIR)), name="samples")

@app.get("/api/health")
async def health_check():
    return {
        "status": "HEALTHY",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "engine_mode": settings.ENGINE_MODE,
        "device": "CPU (Optimized Classical Remote Sensing)",
        "memory_profile": "Ultra-lightweight (<150MB RAM)"
    }
