import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

try:
    from app.main import app
    from app.db.repository import get_repository
    from app.db.schemas import SearchResultSchema
    from app.models.domain import SearchStatus
except ImportError:
    pytest.skip("FastAPI app is not available yet", allow_module_level=True)

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def seed_test_data():
    """Seed test data into repository before running tests"""
    from app.services.search_service import SearchService
    from app.models.requests import SearchRequest
    
    repository = get_repository()
    service = SearchService(repository=repository)
    
    # Create a test search result with id abc123
    test_request = SearchRequest(
        origin="Helsinki",
        travelers=2,
        budget=1000,
        currency="USD",
        date_type="flexible",
    )
    
    # Find packages
    packages = service._find_packages(test_request)
    
    # Create result with specific id
    test_result = SearchResultSchema(
        request_id="abc123",
        status=SearchStatus.processing,
        request=test_request,
        packages=packages,
    )
    repository.save_search_result(test_result)
    yield
    

@pytest.fixture(scope="session")
def test_client():
    return client

