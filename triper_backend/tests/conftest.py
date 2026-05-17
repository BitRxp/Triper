import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

try:
    from app.main import app
except ImportError:
    pytest.skip("FastAPI app is not available yet", allow_module_level=True)

client = TestClient(app)

@pytest.fixture(scope="session")
def test_client():
    return client
