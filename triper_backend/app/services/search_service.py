from typing import List, Optional
from uuid import uuid4

from app.db.repository import InMemoryRepository
from app.db.schemas import PackageSchema, SearchResultSchema
from app.models.domain import SearchStatus
from app.models.requests import SearchRequest


class SearchService:
    def __init__(self, repository: Optional[InMemoryRepository] = None):
        self.repository = repository or InMemoryRepository()

    def search(self, request: SearchRequest) -> SearchResultSchema:
        request_id = str(uuid4())
        packages = self._find_packages(request)
        status = SearchStatus.completed if packages else SearchStatus.error
        result = SearchResultSchema(
            request_id=request_id,
            status=status,
            request=request,
            packages=packages,
        )
        self.repository.save_search_result(result)
        return result

    def load_search_result(self, request_id: str) -> Optional[SearchResultSchema]:
        return self.repository.load_search_result(request_id)

    def _find_packages(self, request: SearchRequest) -> List[PackageSchema]:
        candidates = self.repository.get_seed_packages()
        exact_matches = [p for p in candidates if p.total_price <= request.budget]

        if exact_matches:
            sorted_matches = sorted(exact_matches, key=lambda p: (p.fallback_level, p.total_price))
            return sorted_matches[:4]

        fallback_packages = sorted(candidates, key=lambda p: (p.total_price, p.fallback_level))
        return fallback_packages[:4]
