from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import auth_router, users_router, sessions_router, resume_router
from app.routers.websocket import router as websocket_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Real-time voice-based AI interview preparation system",
    version="1.0.0"
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(sessions_router)
app.include_router(resume_router)
app.include_router(websocket_router)


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "azure_realtime": bool(settings.azure_openai_endpoint),
        "azure_doc_intel": bool(settings.azure_doc_intel_endpoint)
    }
