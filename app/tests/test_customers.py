import pytest


class TestCustomers:
    def test_create_customer(self, client):
        data = {
            "first_name": "Mwansa",
            "last_name": "Phiri",
            "phone": "+260973456789",
            "email": "mwansa@email.com",
            "loyalty_points": 25,
        }
        response = client.post("/api/v1/customers/", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["first_name"] == "Mwansa"
        assert result["last_name"] == "Phiri"
        assert result["loyalty_points"] == 25
        assert "customer_id" in result

    def test_create_customer_defaults(self, client):
        response = client.post(
            "/api/v1/customers/", json={"first_name": "Only", "last_name": "Names"}
        )
        assert response.status_code == 201
        result = response.json()
        assert result["phone"] is None
        assert result["email"] is None
        assert result["loyalty_points"] == 0

    def test_get_all_customers(self, client, sample_customer):
        response = client.get("/api/v1/customers/")
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)
        assert [c["customer_id"] for c in result] == [sample_customer["customer_id"]]

    def test_get_all_customers_empty(self, client):
        response = client.get("/api/v1/customers/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_customer_by_id(self, client, sample_customer):
        customer_id = sample_customer["customer_id"]
        response = client.get(f"/api/v1/customers/{customer_id}")
        assert response.status_code == 200
        result = response.json()
        assert result["customer_id"] == customer_id
        assert result["first_name"] == "Chanda"

    def test_update_customer(self, client, sample_customer):
        customer_id = sample_customer["customer_id"]
        data = {
            "first_name": "Chanda",
            "last_name": "Mulenga-Banda",
            "phone": "+260970000000",
            "email": "chanda.new@email.com",
            "loyalty_points": 40,
        }
        response = client.put(f"/api/v1/customers/{customer_id}", json=data)
        assert response.status_code == 200
        assert response.json()["last_name"] == "Mulenga-Banda"
        stored = client.get(f"/api/v1/customers/{customer_id}").json()
        assert stored["loyalty_points"] == 40

    def test_delete_customer(self, client, sample_customer):
        customer_id = sample_customer["customer_id"]
        assert client.delete(f"/api/v1/customers/{customer_id}").status_code == 204
        assert client.get(f"/api/v1/customers/{customer_id}").status_code == 404

    def test_delete_customer_keeps_their_sales(self, client, sample_sale, sample_customer):
        # customer_id is optional on sales, so history survives customer removal
        assert client.delete(f"/api/v1/customers/{sample_customer['customer_id']}").status_code == 204
        sale = client.get(f"/api/v1/sales/{sample_sale['sale_id']}").json()
        assert sale["customer_id"] is None

    def test_get_customer_not_found(self, client):
        response = client.get("/api/v1/customers/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Customer not found"

    def test_update_customer_not_found(self, client):
        data = {"first_name": "A", "last_name": "B"}
        response = client.put("/api/v1/customers/9999", json=data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Customer not found"

    def test_delete_customer_not_found(self, client):
        response = client.delete("/api/v1/customers/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Customer not found"

    @pytest.mark.parametrize(
        "payload",
        [
            {"last_name": "NoFirst"},
            {"first_name": "NoLast"},
            {"first_name": "", "last_name": "Empty"},
            {"first_name": "Neg", "last_name": "Points", "loyalty_points": -1},
            {"first_name": "Bad", "last_name": "Points", "loyalty_points": "lots"},
            {},
        ],
        ids=["missing-first", "missing-last", "empty-first", "negative-points", "non-numeric-points", "empty-body"],
    )
    def test_create_customer_validation_errors(self, client, payload):
        response = client.post("/api/v1/customers/", json=payload)
        assert response.status_code == 422

    def test_update_customer_invalid_payload(self, client, sample_customer):
        response = client.put(
            f"/api/v1/customers/{sample_customer['customer_id']}", json={"first_name": "Only"}
        )
        assert response.status_code == 422