from fastapi import APIRouter

from app.db.repository import get_repository
from app.models.responses import PackageSummary, PopularPackagesResponse

router = APIRouter()


@router.get("/popular", response_model=PopularPackagesResponse)
def get_popular_packages():
    repository = get_repository()
    packages = repository.get_popular_packages()
    return PopularPackagesResponse(
        packages=[PackageSummary.model_validate(pkg.model_dump()) for pkg in packages]
    )
