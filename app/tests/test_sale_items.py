import pytest
from decimal import Decimal


def _payload(sale, product, **overrides):
    payload = {
        "quantity": 2,
        "unit_price": 12.50,
        "discount": 0,
        "line_total": 25.00,
        "sale_id": sale["sale_id"],
        "product_id": product["product_id"],
    }
    payload.update(overrides)
    return payload


class TestSaleItems:
    def test_create_sale_item(self, client, sample_sale, sample_product):
        data = {
            "quantity": 3,
            "unit_price": 12.50,
            "discount": 1.50,
            "line_total": 36.00,
            "sale_id": sample_sale["sale_id"],
            "product_id": sample_product["product_id"]
        }
        response = client.post("/api/v1/sale-items/", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["quantity"] == 3
        assert Decimal(result["line_total"]) == Decimal("36.00")

    def test_create_sale_item_invalid_product(self, client, sample_sale):
        data = {
            "quantity": 1,
            "unit_price": 10.00,
            "discount": 0,
            "line_total": 10.00,
            "sale_id": sample_sale["sale_id"],
            "product_id": 9999
        }
        response = client.post("/api/v1/sale-items/", json=data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Product does not exist"

    def test_create_sale_item_invalid_sale(self, client, sample_product):
        data = {
            "quantity": 1,
            "unit_price": 10.00,
            "discount": 0,
            "line_total": 10.00,
            "sale_id": 9999,
            "product_id": sample_product["product_id"]
        }
        response = client.post("/api/v1/sale-items/", json=data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Sale does not exist"

    def test_get_all_sale_items(self, client, sample_sale, sample_product):
        data = {
            "quantity": 2,
            "unit_price": 12.50,
            "discount": 0,
            "line_total": 25.00,
            "sale_id": sample_sale["sale_id"],
            "product_id": sample_product["product_id"]
        }
        client.post("/api/v1/sale-items/", json=data)
        response = client.get("/api/v1/sale-items/")
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_get_sale_item_by_id(self, client, sample_sale, sample_product):
        data = {
            "quantity": 1,
            "unit_price": 12.50,
            "discount": 0,
            "line_total": 12.50,
            "sale_id": sample_sale["sale_id"],
            "product_id": sample_product["product_id"]
        }
        create_response = client.post("/api/v1/sale-items/", json=data)
        item_id = create_response.json()["sale_item_id"]
        response = client.get(f"/api/v1/sale-items/{item_id}")
        assert response.status_code == 200
        result = response.json()
        assert result["sale_item_id"] == item_id

    def test_delete_sale_item(self, client, sample_sale, sample_product):
        data = {
            "quantity": 1,
            "unit_price": 12.50,
            "discount": 0,
            "line_total": 12.50,
            "sale_id": sample_sale["sale_id"],
            "product_id": sample_product["product_id"]
        }
        create_response = client.post("/api/v1/sale-items/", json=data)
        item_id = create_response.json()["sale_item_id"]
        response = client.delete(f"/api/v1/sale-items/{item_id}")
        assert response.status_code == 204

    def test_get_sale_item_not_found(self, client):
        response = client.get("/api/v1/sale-items/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Sale item not found"

    def test_create_sale_item_default_discount(self, client, sample_sale, sample_product):
        data = _payload(sample_sale, sample_product)
        del data["discount"]
        response = client.post("/api/v1/sale-items/", json=data)
        assert response.status_code == 201
        assert Decimal(response.json()["discount"]) == Decimal("0")

    @pytest.mark.parametrize("field", ["quantity", "unit_price", "line_total", "sale_id", "product_id"])
    def test_create_sale_item_missing_required_field(self, client, sample_sale, sample_product, field):
        data = _payload(sample_sale, sample_product)
        del data[field]
        assert client.post("/api/v1/sale-items/", json=data).status_code == 422

    @pytest.mark.parametrize(
        "overrides",
        [
            {"quantity": 0},
            {"quantity": -3},
            {"quantity": "two"},
            {"quantity": 1.5},
            {"unit_price": -1},
            {"discount": -1},
            {"line_total": -1},
        ],
        ids=["zero-qty", "negative-qty", "non-numeric-qty", "fractional-qty", "neg-price", "neg-discount", "neg-total"],
    )
    def test_create_sale_item_invalid_values(self, client, sample_sale, sample_product, overrides):
        data = _payload(sample_sale, sample_product, **overrides)
        assert client.post("/api/v1/sale-items/", json=data).status_code == 422

    def test_get_all_sale_items_empty(self, client):
        response = client.get("/api/v1/sale-items/")
        assert response.status_code == 200
        assert response.json() == []

    def test_update_sale_item_persists(self, client, sample_sale_item, sample_sale, sample_product):
        item_id = sample_sale_item["sale_item_id"]
        data = _payload(sample_sale, sample_product, quantity=5, line_total=62.50)
        assert client.put(f"/api/v1/sale-items/{item_id}", json=data).status_code == 200
        stored = client.get(f"/api/v1/sale-items/{item_id}").json()
        assert stored["quantity"] == 5
        assert Decimal(stored["line_total"]) == Decimal("62.50")

    def test_update_sale_item_not_found(self, client, sample_sale, sample_product):
        response = client.put("/api/v1/sale-items/9999", json=_payload(sample_sale, sample_product))
        assert response.status_code == 404
        assert response.json()["detail"] == "Sale item not found"

    def test_update_sale_item_invalid_sale(self, client, sample_sale_item, sample_sale, sample_product):
        data = _payload(sample_sale, sample_product, sale_id=9999)
        response = client.put(f"/api/v1/sale-items/{sample_sale_item['sale_item_id']}", json=data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Sale does not exist"

    def test_update_sale_item_invalid_product(self, client, sample_sale_item, sample_sale, sample_product):
        data = _payload(sample_sale, sample_product, product_id=9999)
        response = client.put(f"/api/v1/sale-items/{sample_sale_item['sale_item_id']}", json=data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Product does not exist"

    def test_update_sale_item_invalid_values(self, client, sample_sale_item, sample_sale, sample_product):
        data = _payload(sample_sale, sample_product, quantity=0)
        response = client.put(f"/api/v1/sale-items/{sample_sale_item['sale_item_id']}", json=data)
        assert response.status_code == 422

    def test_delete_sale_item_removes_it(self, client, sample_sale_item):
        item_id = sample_sale_item["sale_item_id"]
        assert client.delete(f"/api/v1/sale-items/{item_id}").status_code == 204
        assert client.get(f"/api/v1/sale-items/{item_id}").status_code == 404

    def test_delete_sale_item_not_found(self, client):
        response = client.delete("/api/v1/sale-items/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Sale item not found"

    def test_delete_sale_item_keeps_sale_and_product(self, client, sample_sale_item, sample_sale, sample_product):
        client.delete(f"/api/v1/sale-items/{sample_sale_item['sale_item_id']}")
        assert client.get(f"/api/v1/sales/{sample_sale['sale_id']}").status_code == 200
        assert client.get(f"/api/v1/products/{sample_product['product_id']}").status_code == 200