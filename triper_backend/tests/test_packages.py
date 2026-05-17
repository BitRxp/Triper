def test_get_popular_packages_returns_package_list(test_client):
    response = test_client.get("/api/v1/packages/popular")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["packages"], list)
    assert len(data["packages"]) >= 1

    package = data["packages"][0]
    assert package["package_id"]
    assert package["title"]
    assert package["description"]
    assert package["direction"]
