from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.resume import router as resume_router
from app.api.job import router as job_router

app = FastAPI(
    title="AI Job Agent API",
    version="1.0.0",
    description="AI Powered Job Search Assistant"
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(job_router)


@app.get("/")
async def root():
    return {
        "message": "AI Job Agent API Running"
    }