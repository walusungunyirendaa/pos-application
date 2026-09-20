import pytest
from decimal import Decimal


def _payload(sale, **overrides):
    payload = {
        "payment_method": "Cash",
        "amount": 60.00,
        "payment_date": "2026-08-01T10:35:00",
        "transaction_reference": None,
        "status": "Approved",
        "sale_id": sale["sale_id"],
    }
    payload.update(overrides)
    return payload


class TestPayments:
    def test_create_payment(self, client, sample_sale):
        data = {
            "payment_method": "Cash",
            "amount": 60.00,
            "payment_date": "2026-08-01T10:35:00",
            "transaction_reference": None,
            "status": "Approved",
            "sale_id": sample_sale["sale_id"]
        }
        response = client.post("/api/v1/payments/", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["payment_method"] == "Cash"
        assert Decimal(result["amount"]) == Decimal("60.00")

    def test_create_payment_card(self, client, sample_sale):
        data = {
            "payment_method": "Card",
            "amount": 51.00,
            "payment_date": "2026-08-01T10:35:00",
            "transaction_reference": "TXN123456789",
            "status": "Approved",
            "sale_id": sample_sale["sale_id"]
        }
        response = client.post("/api/v1/payments/", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["transaction_reference"] == "TXN123456789"

    def test_create_payment_invalid_sale(self, client):
        data = {
            "payment_method": "Cash",
            "amount": 50.00,
            "payment_date": "2026-08-01T10:35:00",
            "transaction_reference": None,
            "status": "Approved",
            "sale_id": 9999
        }
        response = client.post("/api/v1/payments/", json=data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Sale does not exist"

    def test_get_all_payments(self, client, sample_sale):
        data = {
            "payment_method": "Cash",
            "amount": 60.00,
            "payment_date": "2026-08-01T10:35:00",
            "transaction_reference": None,
            "status": "Approved",
            "sale_id": sample_sale["sale_id"]
        }
        client.post("/api/v1/payments/", json=data)
        response = client.get("/api/v1/payments/")
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)

    def test_delete_payment(self, client, sample_sale):
        data = {
            "payment_method": "Cash",
            "amount": 60.00,
            "payment_date": "2026-08-01T10:35:00",
            "transaction_reference": None,
            "status": "Approved",
            "sale_id": sample_sale["sale_id"]
        }
        create_response = client.post("/api/v1/payments/", json=data)
        payment_id = create_response.json()["payment_id"]
        response = client.delete(f"/api/v1/payments/{payment_id}")
        assert response.status_code == 204

    def test_get_payment_not_found(self, client):
        response = client.get("/api/v1/payments/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Payment not found"

    def test_create_payment_default_status(self, client, sample_sale):
        data = _payload(sample_sale)
        del data["status"]
        response = client.post("/api/v1/payments/", json=data)
        assert response.status_code == 201
        assert response.json()["status"] == "Approved"

    @pytest.mark.parametrize("field", ["payment_method", "amount", "payment_date", "sale_id"])
    def test_create_payment_missing_required_field(self, client, sample_sale, field):
        data = _payload(sample_sale)
        del data[field]
        assert client.post("/api/v1/payments/", json=data).status_code == 422

    @pytest.mark.parametrize(
        "overrides",
        [
            {"amount": 0},
            {"amount": -10},
            {"amount": "sixty"},
            {"payment_method": ""},
            {"payment_date": "yesterday-ish"},
            {"sale_id": "abc"},
        ],
        ids=["zero-amount", "negative-amount", "non-numeric-amount", "empty-method", "bad-date", "non-numeric-sale"],
    )
    def test_create_payment_invalid_values(self, client, sample_sale, overrides):
        data = _payload(sample_sale, **overrides)
        assert client.post("/api/v1/payments/", json=data).status_code == 422

    def test_get_all_payments_empty(self, client):
        response = client.get("/api/v1/payments/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_payments_lists_created(self, client, sample_payment):
        listed = client.get("/api/v1/payments/").json()
        assert [p["payment_id"] for p in listed] == [sample_payment["payment_id"]]

    def test_get_payment_by_id(self, client, sample_payment):
        response = client.get(f"/api/v1/payments/{sample_payment['payment_id']}")
        assert response.status_code == 200
        assert response.json()["payment_id"] == sample_payment["payment_id"]

    def test_update_payment_persists(self, client, sample_payment, sample_sale):
        payment_id = sample_payment["payment_id"]
        data = _payload(sample_sale, payment_method="Card", transaction_reference="TXN-9", amount=45.5)
        assert client.put(f"/api/v1/payments/{payment_id}", json=data).status_code == 200
        stored = client.get(f"/api/v1/payments/{payment_id}").json()
        assert stored["payment_method"] == "Card"
        assert stored["transaction_reference"] == "TXN-9"
        assert Decimal(stored["amount"]) == Decimal("45.50")

    def test_update_payment_not_found(self, client, sample_sale):
        response = client.put("/api/v1/payments/9999", json=_payload(sample_sale))
        assert response.status_code == 404
        assert response.json()["detail"] == "Payment not found"

    def test_update_payment_invalid_sale(self, client, sample_payment, sample_sale):
        data = _payload(sample_sale, sale_id=9999)
        response = client.put(f"/api/v1/payments/{sample_payment['payment_id']}", json=data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Sale does not exist"

    def test_update_payment_invalid_values(self, client, sample_payment, sample_sale):
        data = _payload(sample_sale, amount=-1)
        response = client.put(f"/api/v1/payments/{sample_payment['payment_id']}", json=data)
        assert response.status_code == 422

    def test_delete_payment_removes_it(self, client, sample_payment):
        payment_id = sample_payment["payment_id"]
        assert client.delete(f"/api/v1/payments/{payment_id}").status_code == 204
        assert client.get(f"/api/v1/payments/{payment_id}").status_code == 404

    def test_delete_payment_not_found(self, client):
        response = client.delete("/api/v1/payments/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Payment not found"

    def test_sale_can_have_multiple_payments(self, client, sample_sale):
        for method, amount in (("Cash", 50), ("Card", 61)):
            response = client.post(
                "/api/v1/payments/", json=_payload(sample_sale, payment_method=method, amount=amount)
            )
            assert response.status_code == 201
        assert len(client.get("/api/v1/payments/").json()) == 2