from fastapi import FastAPI
from app.api.v1.api_router import router

app = FastAPI(
    title="Triper Backend",
    description="Budget-first travel finder backend",
    version="0.1.0",
)

app.include_router(router, prefix="/api/v1")
