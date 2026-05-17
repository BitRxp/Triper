from fastapi import APIRouter, HTTPException
from fastapi import status as http_status

from app.db.repository import InMemoryRepository
from app.models.requests import SearchRequest
from app.models.responses import SearchResponse
from app.services.search_service import SearchService

router = APIRouter()
repository = InMemoryRepository()
search_service = SearchService(repository=repository)


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


@router.get("/{request_id}", response_model=SearchResponse)
def get_search_result(request_id: str):
    search_result = search_service.load_search_result(request_id)
    if not search_result:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Search result not found",
        )
    return SearchResponse(
        request_id=search_result.request_id,
        status=search_result.status,
        duration_seconds=int((search_result.updated_at - search_result.created_at).total_seconds()),
        packages=search_result.packages,
    )
