class TestCategories:
    def test_create_category(self, client):
        data = {
            "category_name": "Snacks",
            "description": "Chips and biscuits",
            "is_active": True
        }
        response = client.post("/api/v1/categories/", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["category_name"] == "Snacks"
        assert result["description"] == "Chips and biscuits"
        assert result["is_active"] is True
        assert "category_id" in result

    def test_get_all_categories(self, client, sample_category):
        response = client.get("/api/v1/categories/")
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_get_category_by_id(self, client, sample_category):
        category_id = sample_category["category_id"]
        response = client.get(f"/api/v1/categories/{category_id}")
        assert response.status_code == 200
        result = response.json()
        assert result["category_id"] == category_id
        assert result["category_name"] == "Beverages"

    def test_update_category(self, client, sample_category):
        category_id = sample_category["category_id"]
        data = {
            "category_name": "Soft Drinks",
            "description": "Updated description",
            "is_active": True
        }
        response = client.put(f"/api/v1/categories/{category_id}", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["category_name"] == "Soft Drinks"
        assert result["description"] == "Updated description"

    def test_delete_category(self, client, sample_category):
        category_id = sample_category["category_id"]
        response = client.delete(f"/api/v1/categories/{category_id}")
        assert response.status_code == 204

    def test_get_category_not_found(self, client):
        response = client.get("/api/v1/categories/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"

    def test_create_category_missing_name(self, client):
        data = {"description": "No name", "is_active": True}
        response = client.post("/api/v1/categories/", json=data)
        assert response.status_code == 422
