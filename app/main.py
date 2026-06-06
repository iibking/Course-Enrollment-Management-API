from fastapi import FastAPI
from app.core.config import settings
from app.api.v1 import auth, courses, enrollments


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Feature routers
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(enrollments.router)


@app.get("/", tags=["Health"])
async def health_check():
    """Simple liveness check."""
    return {"status": "ok", "service": settings.PROJECT_NAME}