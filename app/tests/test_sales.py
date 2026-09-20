import pytest
from decimal import Decimal


def _payload(user_id, **overrides):
    payload = {
        "sale_date": "2026-08-01T12:00:00",
        "subtotal": 20.00,
        "tax_amount": 3.20,
        "discount_amount": 0,
        "total_amount": 23.20,
        "status": "Completed",
        "customer_id": None,
        "user_id": user_id,
    }
    payload.update(overrides)
    return payload


class TestSales:
    def test_create_sale(self, client, sample_customer, sample_user):
        data = {
            "sale_date": "2026-08-01T14:00:00",
            "subtotal": 50.00,
            "tax_amount": 8.00,
            "discount_amount": 0,
            "total_amount": 58.00,
            "status": "Completed",
            "customer_id": sample_customer["customer_id"],
            "user_id": sample_user["user_id"]
        }
        response = client.post("/api/v1/sales/", json=data)
        assert response.status_code == 201
        result = response.json()
        assert Decimal(result["subtotal"]) == Decimal("50.00")
        assert Decimal(result["total_amount"]) == Decimal("58.00")
        assert result["status"] == "Completed"

    def test_create_sale_no_customer(self, client, sample_user):
        data = {
            "sale_date": "2026-08-01T15:00:00",
            "subtotal": 25.00,
            "tax_amount": 4.00,
            "discount_amount": 0,
            "total_amount": 29.00,
            "status": "Completed",
            "customer_id": None,
            "user_id": sample_user["user_id"]
        }
        response = client.post("/api/v1/sales/", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["customer_id"] is None

    def test_create_sale_invalid_user(self, client, sample_customer):
        data = {
            "sale_date": "2026-08-01T15:00:00",
            "subtotal": 25.00,
            "tax_amount": 4.00,
            "discount_amount": 0,
            "total_amount": 29.00,
            "status": "Completed",
            "customer_id": sample_customer["customer_id"],
            "user_id": 9999
        }
        response = client.post("/api/v1/sales/", json=data)
        assert response.status_code == 400
        assert response.json()["detail"] == "User does not exist"

    def test_get_all_sales(self, client, sample_sale):
        response = client.get("/api/v1/sales/")
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_get_sale_by_id(self, client, sample_sale):
        sale_id = sample_sale["sale_id"]
        response = client.get(f"/api/v1/sales/{sale_id}")
        assert response.status_code == 200
        result = response.json()
        assert result["sale_id"] == sale_id

    def test_update_sale(self, client, sample_sale, sample_customer, sample_user):
        sale_id = sample_sale["sale_id"]
        data = {
            "sale_date": "2026-08-01T10:30:00",
            "subtotal": 120.00,
            "tax_amount": 19.20,
            "discount_amount": 10.00,
            "total_amount": 129.20,
            "status": "Completed",
            "customer_id": sample_customer["customer_id"],
            "user_id": sample_user["user_id"]
        }
        response = client.put(f"/api/v1/sales/{sale_id}", json=data)
        assert response.status_code == 200
        result = response.json()
        assert Decimal(result["subtotal"]) == Decimal("120.00")

    def test_delete_sale(self, client, sample_sale):
        sale_id = sample_sale["sale_id"]
        response = client.delete(f"/api/v1/sales/{sale_id}")
        assert response.status_code == 204

    def test_get_sale_not_found(self, client):
        response = client.get("/api/v1/sales/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Sale not found"

    def test_create_sale_applies_defaults(self, client, sample_user):
        data = {
            "sale_date": "2026-08-01T16:00:00",
            "subtotal": 10.00,
            "tax_amount": 1.60,
            "total_amount": 11.60,
            "user_id": sample_user["user_id"],
        }
        response = client.post("/api/v1/sales/", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["status"] == "Completed"
        assert Decimal(result["discount_amount"]) == Decimal("0")
        assert result["customer_id"] is None

    def test_create_sale_invalid_customer(self, client, sample_user):
        data = _payload(sample_user["user_id"], customer_id=9999)
        response = client.post("/api/v1/sales/", json=data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Customer does not exist"

    @pytest.mark.parametrize("field", ["sale_date", "subtotal", "tax_amount", "total_amount", "user_id"])
    def test_create_sale_missing_required_field(self, client, sample_user, field):
        data = _payload(sample_user["user_id"])
        del data[field]
        assert client.post("/api/v1/sales/", json=data).status_code == 422

    @pytest.mark.parametrize(
        "overrides",
        [
            {"subtotal": -1},
            {"tax_amount": -0.5},
            {"discount_amount": -2},
            {"total_amount": -10},
            {"sale_date": "not-a-date"},
            {"subtotal": "lots"},
            {"status": ""},
        ],
        ids=["neg-subtotal", "neg-tax", "neg-discount", "neg-total", "bad-date", "non-numeric", "empty-status"],
    )
    def test_create_sale_invalid_values(self, client, sample_user, overrides):
        data = _payload(sample_user["user_id"], **overrides)
        assert client.post("/api/v1/sales/", json=data).status_code == 422

    def test_get_all_sales_empty(self, client):
        response = client.get("/api/v1/sales/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_sales_returns_every_sale(self, client, make_sale):
        ids = {make_sale()["sale_id"], make_sale(total_amount=50)["sale_id"]}
        listed = {s["sale_id"] for s in client.get("/api/v1/sales/").json()}
        assert listed == ids

    def test_update_sale_persists(self, client, sample_sale):
        sale_id = sample_sale["sale_id"]
        data = _payload(sample_sale["user_id"], status="Refunded", total_amount=0)
        assert client.put(f"/api/v1/sales/{sale_id}", json=data).status_code == 200
        stored = client.get(f"/api/v1/sales/{sale_id}").json()
        assert stored["status"] == "Refunded"
        assert Decimal(stored["total_amount"]) == Decimal("0")

    def test_update_sale_not_found(self, client, sample_user):
        response = client.put("/api/v1/sales/9999", json=_payload(sample_user["user_id"]))
        assert response.status_code == 404
        assert response.json()["detail"] == "Sale not found"

    def test_update_sale_invalid_user(self, client, sample_sale):
        data = _payload(9999)
        response = client.put(f"/api/v1/sales/{sample_sale['sale_id']}", json=data)
        assert response.status_code == 400
        assert response.json()["detail"] == "User does not exist"

    def test_update_sale_invalid_customer(self, client, sample_sale):
        data = _payload(sample_sale["user_id"], customer_id=9999)
        response = client.put(f"/api/v1/sales/{sample_sale['sale_id']}", json=data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Customer does not exist"

    def test_update_sale_invalid_values(self, client, sample_sale):
        data = _payload(sample_sale["user_id"], subtotal=-1)
        response = client.put(f"/api/v1/sales/{sample_sale['sale_id']}", json=data)
        assert response.status_code == 422

    def test_delete_sale_removes_it(self, client, sample_sale):
        sale_id = sample_sale["sale_id"]
        assert client.delete(f"/api/v1/sales/{sale_id}").status_code == 204
        assert client.get(f"/api/v1/sales/{sale_id}").status_code == 404

    def test_delete_sale_not_found(self, client):
        response = client.delete("/api/v1/sales/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Sale not found"