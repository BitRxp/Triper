from typing import Dict, List, Optional

from app.db.schemas import DestinationSchema, PackageSchema, SearchResultSchema, FeedbackSchema
from app.db.seeds import POPULAR_DESTINATIONS, SEED_PACKAGES


class InMemoryRepository:
    def __init__(self):
        self._destinations: List[DestinationSchema] = [DestinationSchema(**item) for item in POPULAR_DESTINATIONS]
        self._packages: List[PackageSchema] = [PackageSchema(**item) for item in SEED_PACKAGES]
        self._search_cache: Dict[str, SearchResultSchema] = {}
        self._feedback_cache: Dict[str, FeedbackSchema] = {}

    def get_popular_destinations(self) -> List[DestinationSchema]:
        return self._destinations

    def get_popular_packages(self) -> List[PackageSchema]:
        return self._packages

    def get_seed_packages(self) -> List[PackageSchema]:
        return self._packages

    def save_search_result(self, search_result: SearchResultSchema) -> None:
        self._search_cache[search_result.request_id] = search_result

    def load_search_result(self, request_id: str) -> Optional[SearchResultSchema]:
        return self._search_cache.get(request_id)

    def find_package_by_id(self, package_id: str) -> Optional[PackageSchema]:
        return next((p for p in self._packages if p.package_id == package_id), None)

    def list_search_results(self) -> List[SearchResultSchema]:
        return list(self._search_cache.values())

    def save_feedback(self, feedback: FeedbackSchema) -> None:
        self._feedback_cache[feedback.feedback_id] = feedback

    def list_feedback(self) -> List[FeedbackSchema]:
        return list(self._feedback_cache.values())


# Global singleton instance
_repository_instance: Optional[InMemoryRepository] = None


def get_repository() -> InMemoryRepository:
    """Get or create the global repository instance."""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = InMemoryRepository()
    return _repository_instance

