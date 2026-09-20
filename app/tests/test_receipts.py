import pytest
def _payload(sale, **overrides):
    payload = {
        "receipt_number": "RCP-NEW-001",
        "issued_date": "2026-08-01T10:36:00",
        "file_url": "/receipts/new.pdf",
        "sale_id": sale["sale_id"],
    }
    payload.update(overrides)
    return payload


class TestReceipts:
    def test_create_receipt(self, client, sample_sale):
        data = {
            "receipt_number": "RCP-2026-0001",
            "issued_date": "2026-08-01T10:36:00",
            "file_url": "/receipts/RCP-2026-0001.pdf",
            "sale_id": sample_sale["sale_id"]
        }
        response = client.post("/api/v1/receipts/", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["receipt_number"] == "RCP-2026-0001"

    def test_create_receipt_duplicate_sale(self, client, sample_sale):
        data = {
            "receipt_number": "RCP-2026-0001",
            "issued_date": "2026-08-01T10:36:00",
            "file_url": "/receipts/RCP-2026-0001.pdf",
            "sale_id": sample_sale["sale_id"]
        }
        client.post("/api/v1/receipts/", json=data)
        data2 = {
            "receipt_number": "RCP-2026-0002",
            "issued_date": "2026-08-01T10:36:00",
            "file_url": "/receipts/RCP-2026-0002.pdf",
            "sale_id": sample_sale["sale_id"]
        }
        response = client.post("/api/v1/receipts/", json=data2)
        assert response.status_code == 400
        assert response.json()["detail"] == "Receipt already exists for this sale"

    def test_create_receipt_invalid_sale(self, client):
        data = {
            "receipt_number": "RCP-2026-0003",
            "issued_date": "2026-08-01T10:36:00",
            "file_url": "/receipts/RCP-2026-0003.pdf",
            "sale_id": 9999
        }
        response = client.post("/api/v1/receipts/", json=data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Sale does not exist"

    def test_get_receipt_by_id(self, client, sample_sale):
        data = {
            "receipt_number": "RCP-TEST-001",
            "issued_date": "2026-08-01T10:36:00",
            "file_url": "/receipts/test.pdf",
            "sale_id": sample_sale["sale_id"]
        }
        create_response = client.post("/api/v1/receipts/", json=data)
        receipt_id = create_response.json()["receipt_id"]
        response = client.get(f"/api/v1/receipts/{receipt_id}")
        assert response.status_code == 200
        result = response.json()
        assert result["receipt_id"] == receipt_id

    def test_delete_receipt(self, client, sample_sale):
        data = {
            "receipt_number": "RCP-DELETE-001",
            "issued_date": "2026-08-01T10:36:00",
            "file_url": "/receipts/delete.pdf",
            "sale_id": sample_sale["sale_id"]
        }
        create_response = client.post("/api/v1/receipts/", json=data)
        receipt_id = create_response.json()["receipt_id"]
        response = client.delete(f"/api/v1/receipts/{receipt_id}")
        assert response.status_code == 204

    def test_get_receipt_not_found(self, client):
        response = client.get("/api/v1/receipts/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Receipt not found"

    def test_create_receipt_without_file_url(self, client, sample_sale):
        data = _payload(sample_sale)
        del data["file_url"]
        response = client.post("/api/v1/receipts/", json=data)
        assert response.status_code == 201
        assert response.json()["file_url"] is None

    def test_create_receipt_duplicate_number(self, client, sample_receipt, make_sale):
        other_sale = make_sale()
        data = _payload(other_sale, receipt_number=sample_receipt["receipt_number"])
        response = client.post("/api/v1/receipts/", json=data)
        assert response.status_code == 409
        assert len(client.get("/api/v1/receipts/").json()) == 1

    @pytest.mark.parametrize("field", ["receipt_number", "issued_date", "sale_id"])
    def test_create_receipt_missing_required_field(self, client, sample_sale, field):
        data = _payload(sample_sale)
        del data[field]
        assert client.post("/api/v1/receipts/", json=data).status_code == 422

    @pytest.mark.parametrize(
        "overrides",
        [{"receipt_number": ""}, {"issued_date": "soon"}, {"sale_id": "abc"}],
        ids=["empty-number", "bad-date", "non-numeric-sale"],
    )
    def test_create_receipt_invalid_values(self, client, sample_sale, overrides):
        data = _payload(sample_sale, **overrides)
        assert client.post("/api/v1/receipts/", json=data).status_code == 422

    def test_get_all_receipts_empty(self, client):
        response = client.get("/api/v1/receipts/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_receipts_lists_created(self, client, sample_receipt):
        listed = client.get("/api/v1/receipts/").json()
        assert [r["receipt_id"] for r in listed] == [sample_receipt["receipt_id"]]

    def test_update_receipt_persists(self, client, sample_receipt, sample_sale):
        receipt_id = sample_receipt["receipt_id"]
        data = _payload(sample_sale, receipt_number="RCP-2026-0001", file_url="/receipts/new.pdf")
        assert client.put(f"/api/v1/receipts/{receipt_id}", json=data).status_code == 200
        assert client.get(f"/api/v1/receipts/{receipt_id}").json()["file_url"] == "/receipts/new.pdf"

    def test_update_receipt_move_to_free_sale(self, client, sample_receipt, make_sale):
        other_sale = make_sale()
        data = _payload(other_sale, receipt_number="RCP-2026-0001")
        response = client.put(f"/api/v1/receipts/{sample_receipt['receipt_id']}", json=data)
        assert response.status_code == 200
        assert response.json()["sale_id"] == other_sale["sale_id"]

    def test_update_receipt_not_found(self, client, sample_sale):
        response = client.put("/api/v1/receipts/9999", json=_payload(sample_sale))
        assert response.status_code == 404
        assert response.json()["detail"] == "Receipt not found"

    def test_update_receipt_invalid_sale(self, client, sample_receipt, sample_sale):
        data = _payload(sample_sale, sale_id=9999)
        response = client.put(f"/api/v1/receipts/{sample_receipt['receipt_id']}", json=data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Sale does not exist"

    def test_update_receipt_to_sale_that_already_has_one(self, client, sample_receipt, make_sale):
        other_sale = make_sale()
        client.post("/api/v1/receipts/", json=_payload(other_sale, receipt_number="RCP-SECOND"))
        data = _payload(other_sale, receipt_number="RCP-2026-0001")
        response = client.put(f"/api/v1/receipts/{sample_receipt['receipt_id']}", json=data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Receipt already exists for this sale"

    def test_update_receipt_invalid_values(self, client, sample_receipt, sample_sale):
        data = _payload(sample_sale, receipt_number="")
        response = client.put(f"/api/v1/receipts/{sample_receipt['receipt_id']}", json=data)
        assert response.status_code == 422

    def test_delete_receipt_removes_it(self, client, sample_receipt):
        receipt_id = sample_receipt["receipt_id"]
        assert client.delete(f"/api/v1/receipts/{receipt_id}").status_code == 204
        assert client.get(f"/api/v1/receipts/{receipt_id}").status_code == 404

    def test_delete_receipt_not_found(self, client):
        response = client.delete("/api/v1/receipts/9999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Receipt not found"

    def test_deleting_receipt_frees_the_sale_for_a_new_one(self, client, sample_receipt, sample_sale):
        client.delete(f"/api/v1/receipts/{sample_receipt['receipt_id']}")
        response = client.post("/api/v1/receipts/", json=_payload(sample_sale))
        assert response.status_code == 201