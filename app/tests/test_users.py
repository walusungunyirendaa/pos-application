import pytest


class TestUsers:
    def test_create_user(self, client):
        data = {
            "username": "manager01",
            "password": "managerpass456",
            "full_name": "Bob Zulu",
            "role": "Manager",
            "email": "bob@store.com",
            "is_active": True
        }
        response = client.post("/api/v1/users/", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["username"] == "manager01"
        assert result["full_name"] == "Bob Zulu"
        assert result["role"] == "Manager"
        assert "password" not in result
        assert "password_hash" not in result

    def test_get_all_users(self, client, sample_user):
        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_get_user_by_id(self, client, sample_user):
        user_id = sample_user["user_id"]
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        result = response.json()
        assert result["user_id"] == user_id
        assert result["username"] == "cashier01"

    def test_update_user(self, client, sample_user):
        user_id = sample_user["user_id"]
        data = {
            "username": "cashier01",
            "password": "newpassword789",
            "full_name": "Alice Banda Updated",
            "role": "Senior Cashier",
            "email": "alice.new@store.com",
            "is_active": True
        }
        response = client.put(f"/api/v1/users/{user_id}", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["full_name"] == "Alice Banda Updated"

    def test_delete_user(self, client, sample_user):
        user_id = sample_user["user_id"]
        response = client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 204

    def test_get_user_not_found(self, client):
        response = client.get("/api/v1/users/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_create_user_duplicate_username(self, client, sample_user):
        data = {
            "username": "cashier01",
            "password": "anotherpass",
            "full_name": "Someone Else",
            "role": "Cashier",
        }
        response = client.post("/api/v1/users/", json=data)
        assert response.status_code == 409

    def test_create_user_defaults(self, client):
        data = {"username": "bare", "password": "pw", "full_name": "Bare User", "role": "Cashier"}
        result = client.post("/api/v1/users/", json=data).json()
        assert result["is_active"] is True
        assert result["email"] is None

    def test_password_never_returned(self, client, sample_user):
        listing = client.get("/api/v1/users/").json()
        single = client.get(f"/api/v1/users/{sample_user['user_id']}").json()
        for user in [*listing, single]:
            assert "password" not in user
            assert "password_hash" not in user

    def test_update_user_not_found(self, client):
        data = {"username": "ghost", "password": "pw", "full_name": "G", "role": "Cashier"}
        response = client.put("/api/v1/users/9999", json=data)
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_update_user_to_taken_username(self, client, sample_user):
        other = client.post("/api/v1/users/", json={
            "username": "other", "password": "pw", "full_name": "Other", "role": "Cashier",
        }).json()
        data = {"username": "cashier01", "password": "pw", "full_name": "Other", "role": "Cashier"}
        response = client.put(f"/api/v1/users/{other['user_id']}", json=data)
        assert response.status_code == 409

    def test_delete_user_removes_it(self, client, sample_user):
        user_id = sample_user["user_id"]
        assert client.delete(f"/api/v1/users/{user_id}").status_code == 204
        assert client.get(f"/api/v1/users/{user_id}").status_code == 404

    def test_delete_user_not_found(self, client):
        response = client.delete("/api/v1/users/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_delete_user_with_sales_is_rejected(self, client, sample_sale, sample_user):
        response = client.delete(f"/api/v1/users/{sample_user['user_id']}")
        assert response.status_code == 409
        assert client.get(f"/api/v1/users/{sample_user['user_id']}").status_code == 200

    @pytest.mark.parametrize(
        "missing_field", ["username", "password", "full_name", "role"]
    )
    def test_create_user_missing_required_field(self, client, missing_field):
        data = {"username": "u1", "password": "pw", "full_name": "U One", "role": "Cashier"}
        del data[missing_field]
        response = client.post("/api/v1/users/", json=data)
        assert response.status_code == 422

    @pytest.mark.parametrize("field", ["username", "password", "full_name", "role"])
    def test_create_user_empty_required_field(self, client, field):
        data = {"username": "u1", "password": "pw", "full_name": "U One", "role": "Cashier"}
        data[field] = ""
        response = client.post("/api/v1/users/", json=data)
        assert response.status_code == 422