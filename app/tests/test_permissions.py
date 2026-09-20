import pytest

CATEGORY = {"category_name": "Snacks", "description": "x", "is_active": True}


def _product(category_id):
    return {"sku": "P-RBAC", "name": "RBAC", "price": 1, "category_id": category_id}


def _sale(user_id):
    return {
        "sale_date": "2026-08-01T12:00:00", "subtotal": 1, "tax_amount": 0,
        "total_amount": 1, "user_id": user_id,
    }


class TestAnonymousAccess:
    @pytest.mark.parametrize(
        "method, path",
        [
            ("post", "/api/v1/categories/"),
            ("put", "/api/v1/categories/1"),
            ("delete", "/api/v1/categories/1"),
            ("post", "/api/v1/products/"),
            ("put", "/api/v1/products/1"),
            ("delete", "/api/v1/products/1"),
            ("post", "/api/v1/sales/"),
            ("put", "/api/v1/sales/1"),
            ("delete", "/api/v1/sales/1"),
        ],
    )
    def test_protected_endpoints_require_a_token(self, anon_client, method, path):
        response = getattr(anon_client, method)(path, **({} if method == "delete" else {"json": {}}))
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"


class TestCategoryPermissions:
    @pytest.mark.parametrize("role, expected", [("Admin", 201), ("Manager", 403), ("Cashier", 403)])
    def test_create_category(self, anon_client, auth_headers, role, expected):
        response = anon_client.post("/api/v1/categories/", json=CATEGORY, headers=auth_headers(role))
        assert response.status_code == expected

    @pytest.mark.parametrize("role, expected", [("Admin", 204), ("Manager", 403), ("Cashier", 403)])
    def test_delete_category(self, anon_client, client, auth_headers, sample_category, role, expected):
        response = anon_client.delete(
            f"/api/v1/categories/{sample_category['category_id']}", headers=auth_headers(role)
        )
        assert response.status_code == expected

    def test_forbidden_response_explains_why(self, anon_client, auth_headers):
        response = anon_client.post("/api/v1/categories/", json=CATEGORY, headers=auth_headers("Cashier"))
        assert response.json()["detail"] == "Admin privileges required"


class TestProductPermissions:
    @pytest.mark.parametrize("role, expected", [("Admin", 201), ("Manager", 201), ("Cashier", 403)])
    def test_create_product(self, anon_client, auth_headers, sample_category, role, expected):
        response = anon_client.post(
            "/api/v1/products/", json=_product(sample_category["category_id"]), headers=auth_headers(role)
        )
        assert response.status_code == expected

    @pytest.mark.parametrize("role, expected", [("Admin", 204), ("Manager", 204), ("Cashier", 403)])
    def test_delete_product(self, anon_client, auth_headers, sample_product, role, expected):
        response = anon_client.delete(
            f"/api/v1/products/{sample_product['product_id']}", headers=auth_headers(role)
        )
        assert response.status_code == expected


class TestSalePermissions:
    @pytest.mark.parametrize("role", ["Admin", "Manager", "Cashier"])
    def test_every_staff_role_can_record_a_sale(self, anon_client, auth_headers, sample_user, role):
        response = anon_client.post(
            "/api/v1/sales/", json=_sale(sample_user["user_id"]), headers=auth_headers(role)
        )
        assert response.status_code == 201

    @pytest.mark.parametrize("role, expected", [("Admin", 204), ("Manager", 204), ("Cashier", 403)])
    def test_delete_sale(self, anon_client, auth_headers, sample_sale, role, expected):
        response = anon_client.delete(
            f"/api/v1/sales/{sample_sale['sale_id']}", headers=auth_headers(role)
        )
        assert response.status_code == expected

    def test_unknown_role_is_rejected(self, anon_client, auth_headers, sample_user):
        response = anon_client.post(
            "/api/v1/sales/", json=_sale(sample_user["user_id"]), headers=auth_headers("Intern")
        )
        assert response.status_code == 403


class TestInactiveAccounts:
    def test_inactive_admin_is_locked_out(self, anon_client, auth_headers):
        response = anon_client.post(
            "/api/v1/categories/", json=CATEGORY, headers=auth_headers("Admin", is_active=False)
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Inactive user account"
