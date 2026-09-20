import pytest

RESOURCES = [
    "categories", "suppliers", "products", "users", "customers",
    "sales", "sale-items", "payments", "receipts",
]


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Retail POS System API", "status": "running"}


def test_docs_are_served(client):
    assert client.get("/docs").status_code == 200


def test_unknown_route_returns_404(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404


def test_routes_are_only_mounted_under_api_prefix(client):
    assert client.get("/categories/").status_code == 404
    assert client.get("/api/v1/categories/").status_code == 200


@pytest.mark.parametrize("resource", RESOURCES)
def test_every_resource_is_registered(client, resource):
    paths = client.get("/openapi.json").json()["paths"]
    assert f"/api/v1/{resource}/" in paths
    assert f"/api/v1/{resource}/{{" in "".join(paths)


@pytest.mark.parametrize("resource", RESOURCES)
def test_malformed_id_is_a_validation_error(client, resource):
    assert client.get(f"/api/v1/{resource}/not-a-number").status_code == 422


@pytest.mark.parametrize("resource", RESOURCES)
def test_empty_body_is_a_validation_error(client, resource):
    assert client.post(f"/api/v1/{resource}/", json={}).status_code == 422