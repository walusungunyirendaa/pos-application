class TestRelationships:
    def test_cascade_delete_sale_removes_items(self, client, sample_sale, sample_product):
        item_data = {
            "quantity": 2,
            "unit_price": 12.50,
            "discount": 0,
            "line_total": 25.00,
            "sale_id": sample_sale["sale_id"],
            "product_id": sample_product["product_id"]
        }
        client.post("/api/v1/sale-items/", json=item_data)
        response = client.delete(f"/api/v1/sales/{sample_sale['sale_id']}")
        assert response.status_code == 204
        items_response = client.get("/api/v1/sale-items/")
        assert items_response.json() == []

    def test_cascade_delete_sale_removes_payments(self, client, sample_sale):
        payment_data = {
            "payment_method": "Cash",
            "amount": 60.00,
            "payment_date": "2026-08-01T10:35:00",
            "transaction_reference": None,
            "status": "Approved",
            "sale_id": sample_sale["sale_id"]
        }
        client.post("/api/v1/payments/", json=payment_data)
        response = client.delete(f"/api/v1/sales/{sample_sale['sale_id']}")
        assert response.status_code == 204
        payments_response = client.get("/api/v1/payments/")
        assert payments_response.json() == []

    def test_cascade_delete_sale_removes_receipt(self, client, sample_sale):
        receipt_data = {
            "receipt_number": "RCP-CASCADE-001",
            "issued_date": "2026-08-01T10:36:00",
            "file_url": "/receipts/cascade.pdf",
            "sale_id": sample_sale["sale_id"]
        }
        client.post("/api/v1/receipts/", json=receipt_data)
        response = client.delete(f"/api/v1/sales/{sample_sale['sale_id']}")
        assert response.status_code == 204
        receipts_response = client.get("/api/v1/receipts/")
        assert receipts_response.json() == []

    def test_deleting_a_sale_removes_all_children_but_keeps_reference_data(
        self, client, sample_sale_item, sample_payment, sample_receipt,
        sample_sale, sample_product, sample_customer, sample_user,
    ):
        assert client.delete(f"/api/v1/sales/{sample_sale['sale_id']}").status_code == 204

        assert client.get("/api/v1/sale-items/").json() == []
        assert client.get("/api/v1/payments/").json() == []
        assert client.get("/api/v1/receipts/").json() == []
        assert client.get(f"/api/v1/products/{sample_product['product_id']}").status_code == 200
        assert client.get(f"/api/v1/customers/{sample_customer['customer_id']}").status_code == 200
        assert client.get(f"/api/v1/users/{sample_user['user_id']}").status_code == 200

    def test_deleting_one_sale_does_not_touch_another_sales_children(
        self, client, make_sale, sample_product
    ):
        first, second = make_sale(), make_sale()
        for sale in (first, second):
            client.post("/api/v1/sale-items/", json={
                "quantity": 1, "unit_price": 12.5, "discount": 0, "line_total": 12.5,
                "sale_id": sale["sale_id"], "product_id": sample_product["product_id"],
            })

        client.delete(f"/api/v1/sales/{first['sale_id']}")

        remaining = client.get("/api/v1/sale-items/").json()
        assert [item["sale_id"] for item in remaining] == [second["sale_id"]]

    def test_product_and_category_link(self, client, sample_product, sample_category):
        assert sample_product["category_id"] == sample_category["category_id"]
        products = client.get("/api/v1/products/").json()
        assert products[0]["category_id"] == sample_category["category_id"]