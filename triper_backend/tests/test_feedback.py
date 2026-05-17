def test_feedback_endpoint_accepts_request(test_client):
    payload = {
        "request_id": "abc123",
        "package_id": "opt-001",
        "rating": 4,
        "comment": "I liked the option, but I would like to see more beach trips",
        "improvement_suggestions": ["more beach destinations"],
    }

    response = test_client.post("/api/v1/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["message"], str)
