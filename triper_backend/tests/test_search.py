def test_search_post_returns_processing(test_client):
    payload = {
        "origin": "Helsinki",
        "travelers": 2,
        "budget": 1000,
        "currency": "USD",
        "date_type": "flexible",
        "date_range": {"from": "2025-08-01", "to": "2025-08-31"},
        "duration": {"min_days": 7, "max_days": 10},
        "preferences": ["sea", "architecture"],
        "mood": "surprise",
    }

    response = test_client.post("/api/v1/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processing"
    assert isinstance(data["request_id"], str)
    assert isinstance(data["eta_seconds"], int)
    assert isinstance(data["summary"], str)
    assert isinstance(data["packages"], list)


def test_get_search_by_request_id_returns_completed_package(test_client):
    response = test_client.get("/api/v1/search/abc123")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["request_id"] == "abc123"
    assert isinstance(data["packages"], list)
    assert len(data["packages"]) >= 1

    package = data["packages"][0]
    assert package["package_id"]
    assert package["title"]
    assert package["direction"]
    assert package["total_price"] >= 0
    assert package["currency"]
    assert package["fallback_level"] >= 0
    assert isinstance(package["budget_breakdown"], dict)
    assert "transport" in package["budget_breakdown"]
    assert "accommodation" in package["budget_breakdown"]
