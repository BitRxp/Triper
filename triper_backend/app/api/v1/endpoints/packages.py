from fastapi import APIRouter

from app.db.repository import InMemoryRepository
from app.models.responses import PackageSummary, PopularPackagesResponse

router = APIRouter()
repository = InMemoryRepository()


@router.get("/popular", response_model=PopularPackagesResponse)
def get_popular_packages():
    packages = repository.get_popular_packages()
    return PopularPackagesResponse(
        packages=[PackageSummary.model_validate(pkg.model_dump()) for pkg in packages]
    )
