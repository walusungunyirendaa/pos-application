import pytest


from decimal import Decimal


def _payload(category_id, **overrides):
    payload = {
        "sku": "NEW001",
        "name": "New Product",
        "price": 5.00,
        "cost_price": 3.00,
        "quantity_in_stock": 10,
        "reorder_level": 2,
        "is_active": True,
        "category_id": category_id,
        "supplier_id": None,
    }
    payload.update(overrides)
    return payload


class TestProducts:
    def test_create_product(self, client, sample_category, sample_supplier):
        data = {
            "sku": "PEP001",
            "name": "Pepsi 500ml",
            "price": 11.00,
            "cost_price": 7.50,
            "quantity_in_stock": 80,
            "reorder_level": 15,
            "is_active": True,
            "category_id": sample_category["category_id"],
            "supplier_id": sample_supplier["supplier_id"]
        }
        response = client.post("/api/v1/products/", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["sku"] == "PEP001"
        assert result["name"] == "Pepsi 500ml"
        assert Decimal(result["price"]) == Decimal("11.00")
        assert result["quantity_in_stock"] == 80

    def test_create_product_invalid_category(self, client, sample_supplier):
        data = {
            "sku": "INVALID",
            "name": "Test",
            "price": 10.00,
            "quantity_in_stock": 10,
            "is_active": True,
            "category_id": 9999,
            "supplier_id": sample_supplier["supplier_id"]
        }
        response = client.post("/api/v1/products/", json=data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Category does not exist"

    def test_get_all_products(self, client, sample_product):
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_get_product_by_id(self, client, sample_product):
        product_id = sample_product["product_id"]
        response = client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == 200
        result = response.json()
        assert result["product_id"] == product_id
        assert result["sku"] == "CC001"

    def test_update_product(self, client, sample_product, sample_category):
        product_id = sample_product["product_id"]
        data = {
            "sku": "CC001",
            "name": "Coca-Cola 500ml Updated",
            "price": 13.00,
            "cost_price": 8.50,
            "quantity_in_stock": 150,
            "reorder_level": 25,
            "is_active": True,
            "category_id": sample_category["category_id"],
            "supplier_id": sample_product["supplier_id"]
        }
        response = client.put(f"/api/v1/products/{product_id}", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["name"] == "Coca-Cola 500ml Updated"
        assert Decimal(result["price"]) == Decimal("13.00")

    def test_delete_product(self, client, sample_product):
        product_id = sample_product["product_id"]
        response = client.delete(f"/api/v1/products/{product_id}")
        assert response.status_code == 204

    def test_get_product_not_found(self, client):
        response = client.get("/api/v1/products/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"

    def test_create_product_without_supplier(self, client, sample_category):
        response = client.post("/api/v1/products/", json=_payload(sample_category["category_id"]))
        assert response.status_code == 201
        assert response.json()["supplier_id"] is None

    def test_create_product_applies_defaults(self, client, sample_category):
        data = {
            "sku": "MIN001", "name": "Minimal", "price": 1.0,
            "category_id": sample_category["category_id"],
        }
        result = client.post("/api/v1/products/", json=data).json()
        assert result["quantity_in_stock"] == 0
        assert result["is_active"] is True
        assert result["cost_price"] is None
        assert result["reorder_level"] is None

    def test_create_product_zero_price_allowed(self, client, sample_category):
        data = _payload(sample_category["category_id"], price=0)
        assert client.post("/api/v1/products/", json=data).status_code == 201

    def test_create_product_invalid_supplier(self, client, sample_category):
        data = _payload(sample_category["category_id"], supplier_id=9999)
        response = client.post("/api/v1/products/", json=data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Supplier does not exist"

    def test_create_product_duplicate_sku(self, client, sample_product):
        data = _payload(sample_product["category_id"], sku=sample_product["sku"])
        response = client.post("/api/v1/products/", json=data)
        assert response.status_code == 409
        skus = [p["sku"] for p in client.get("/api/v1/products/").json()]
        assert skus.count(sample_product["sku"]) == 1

    @pytest.mark.parametrize("field", ["sku", "name", "price", "category_id"])
    def test_create_product_missing_required_field(self, client, sample_category, field):
        data = _payload(sample_category["category_id"])
        del data[field]
        assert client.post("/api/v1/products/", json=data).status_code == 422

    @pytest.mark.parametrize(
        "overrides",
        [
            {"sku": ""},
            {"name": ""},
            {"price": -0.01},
            {"price": "free"},
            {"cost_price": -1},
            {"quantity_in_stock": -1},
            {"quantity_in_stock": 1.5},
            {"reorder_level": -1},
            {"is_active": "maybe"},
        ],
        ids=[
            "empty-sku", "empty-name", "negative-price", "non-numeric-price", "negative-cost",
            "negative-stock", "fractional-stock", "negative-reorder", "bad-is_active",
        ],
    )
    def test_create_product_invalid_values(self, client, sample_category, overrides):
        data = _payload(sample_category["category_id"], **overrides)
        assert client.post("/api/v1/products/", json=data).status_code == 422

    def test_get_all_products_empty(self, client):
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        assert response.json() == []

    def test_update_product_persists(self, client, sample_product):
        product_id = sample_product["product_id"]
        data = _payload(
            sample_product["category_id"], supplier_id=sample_product["supplier_id"],
            sku="CC001", name="Renamed", quantity_in_stock=7,
        )
        assert client.put(f"/api/v1/products/{product_id}", json=data).status_code == 200
        stored = client.get(f"/api/v1/products/{product_id}").json()
        assert stored["name"] == "Renamed"
        assert stored["quantity_in_stock"] == 7

    def test_update_product_not_found(self, client, sample_category):
        data = _payload(sample_category["category_id"])
        response = client.put("/api/v1/products/9999", json=data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"

    def test_update_product_invalid_category(self, client, sample_product):
        data = _payload(9999, sku="CC001")
        response = client.put(f"/api/v1/products/{sample_product['product_id']}", json=data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Category does not exist"

    def test_update_product_invalid_supplier(self, client, sample_product):
        data = _payload(sample_product["category_id"], sku="CC001", supplier_id=9999)
        response = client.put(f"/api/v1/products/{sample_product['product_id']}", json=data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Supplier does not exist"

    def test_update_product_duplicate_sku(self, client, sample_product):
        other = client.post(
            "/api/v1/products/", json=_payload(sample_product["category_id"], sku="OTHER1")
        ).json()
        data = _payload(sample_product["category_id"], sku=sample_product["sku"])
        response = client.put(f"/api/v1/products/{other['product_id']}", json=data)
        assert response.status_code == 409

    def test_update_product_invalid_values(self, client, sample_product):
        data = _payload(sample_product["category_id"], sku="CC001", price=-5)
        response = client.put(f"/api/v1/products/{sample_product['product_id']}", json=data)
        assert response.status_code == 422

    def test_delete_product_removes_it(self, client, sample_product):
        product_id = sample_product["product_id"]
        assert client.delete(f"/api/v1/products/{product_id}").status_code == 204
        assert client.get(f"/api/v1/products/{product_id}").status_code == 404

    def test_delete_product_not_found(self, client):
        response = client.delete("/api/v1/products/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"

    def test_delete_product_sold_in_a_sale_is_rejected(self, client, sample_sale_item, sample_product):
        response = client.delete(f"/api/v1/products/{sample_product['product_id']}")
        assert response.status_code == 409
        assert client.get(f"/api/v1/products/{sample_product['product_id']}").status_code == 200