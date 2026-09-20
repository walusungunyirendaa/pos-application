import pytest


class TestSuppliers:
    def test_create_supplier(self, client):
        data = {
            "supplier_name": "PepsiCo",
            "contact_person": "Jane Doe",
            "phone": "+260979876543",
            "email": "jane@pepsi.com",
            "address": "456 Business Park"
        }
        response = client.post("/api/v1/suppliers/", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["supplier_name"] == "PepsiCo"
        assert result["phone"] == "+260979876543"

    def test_get_all_suppliers(self, client, sample_supplier):
        response = client.get("/api/v1/suppliers/")
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_get_supplier_by_id(self, client, sample_supplier):
        supplier_id = sample_supplier["supplier_id"]
        response = client.get(f"/api/v1/suppliers/{supplier_id}")
        assert response.status_code == 200
        result = response.json()
        assert result["supplier_id"] == supplier_id

    def test_update_supplier(self, client, sample_supplier):
        supplier_id = sample_supplier["supplier_id"]
        data = {
            "supplier_name": "Coca-Cola Ltd",
            "contact_person": "Updated Person",
            "phone": "+260971234567",
            "email": "updated@cocacola.com",
            "address": "New Address"
        }
        response = client.put(f"/api/v1/suppliers/{supplier_id}", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["supplier_name"] == "Coca-Cola Ltd"

    def test_delete_supplier(self, client, sample_supplier):
        supplier_id = sample_supplier["supplier_id"]
        response = client.delete(f"/api/v1/suppliers/{supplier_id}")
        assert response.status_code == 204

    def test_get_supplier_not_found(self, client):
        response = client.get("/api/v1/suppliers/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Supplier not found"

    def test_create_supplier_minimal(self, client):
        response = client.post(
            "/api/v1/suppliers/", json={"supplier_name": "Bare Minimum Ltd", "phone": "0971"}
        )
        assert response.status_code == 201
        result = response.json()
        assert result["contact_person"] is None
        assert result["email"] is None
        assert result["address"] is None

    def test_get_all_suppliers_empty(self, client):
        response = client.get("/api/v1/suppliers/")
        assert response.status_code == 200
        assert response.json() == []

    def test_update_supplier_persists(self, client, sample_supplier):
        supplier_id = sample_supplier["supplier_id"]
        data = {"supplier_name": "Renamed Ltd", "phone": "0000"}
        assert client.put(f"/api/v1/suppliers/{supplier_id}", json=data).status_code == 200
        stored = client.get(f"/api/v1/suppliers/{supplier_id}").json()
        assert stored["supplier_name"] == "Renamed Ltd"
        assert stored["contact_person"] is None

    def test_update_supplier_not_found(self, client):
        data = {"supplier_name": "X", "phone": "1"}
        response = client.put("/api/v1/suppliers/9999", json=data)
        assert response.status_code == 404
        assert response.json()["detail"] == "Supplier not found"

    def test_update_supplier_invalid_payload(self, client, sample_supplier):
        response = client.put(
            f"/api/v1/suppliers/{sample_supplier['supplier_id']}", json={"supplier_name": "No phone"}
        )
        assert response.status_code == 422

    def test_delete_supplier_removes_it(self, client, sample_supplier):
        supplier_id = sample_supplier["supplier_id"]
        assert client.delete(f"/api/v1/suppliers/{supplier_id}").status_code == 204
        assert client.get(f"/api/v1/suppliers/{supplier_id}").status_code == 404

    def test_delete_supplier_not_found(self, client):
        response = client.delete("/api/v1/suppliers/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Supplier not found"

    def test_delete_supplier_detaches_products(self, client, sample_product):
        supplier_id = sample_product["supplier_id"]
        assert client.delete(f"/api/v1/suppliers/{supplier_id}").status_code == 204
        product = client.get(f"/api/v1/products/{sample_product['product_id']}").json()
        assert product["supplier_id"] is None

    @pytest.mark.parametrize(
        "payload",
        [
            {"phone": "0971"},
            {"supplier_name": "No phone"},
            {"supplier_name": "", "phone": "0971"},
            {"supplier_name": "Ok", "phone": ""},
            {"supplier_name": ["not", "a", "string"], "phone": "0971"},
        ],
        ids=["missing-name", "missing-phone", "empty-name", "empty-phone", "wrong-type"],
    )
    def test_create_supplier_validation_errors(self, client, payload):
        response = client.post("/api/v1/suppliers/", json=payload)
        assert response.status_code == 422