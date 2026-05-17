from fastapi import APIRouter
from app.api.v1.endpoints import health, packages, search, feedback

router = APIRouter()
router.include_router(search.router, prefix="/search", tags=["search"])
router.include_router(packages.router, prefix="/packages", tags=["packages"])
router.include_router(health.router, prefix="", tags=["health"])
router.include_router(feedback.router, prefix="", tags=["feedback"])
