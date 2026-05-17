from fastapi import APIRouter

from app.models.requests import SearchRequest
from app.models.responses import SearchResponse
from app.services.search_service import SearchService

router = APIRouter()
search_service = SearchService()


@router.post("", response_model=SearchResponse)
def create_search(request: SearchRequest):
    search_result = search_service.search(request)
    return SearchResponse(
        request_id=search_result.request_id,
        status=search_result.status,
        eta_seconds=5,
        summary="We are preparing ready-made holiday options within your budget",
        packages=search_result.packages,
    )
