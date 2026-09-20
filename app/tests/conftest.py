import itertools
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite://"
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

from database import Base, get_db  
from main import app  
from models.user import User  
from services.auth_service import create_access_token  

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
    dbapi_connection.execute("PRAGMA foreign_keys=ON")


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def _bearer(user_id: int) -> dict:
    return {"Authorization": f"Bearer {create_access_token({'sub': str(user_id)})}"}


def _create(client, resource: str, payload: dict) -> dict:
    response = client.post(f"/api/v1/{resource}/", json=payload)
    assert response.status_code == 201, (
        f"fixture setup failed for '{resource}': {response.status_code} {response.text}"
    )
    return response.json()



@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db

    with TestingSessionLocal() as db:
        admin = User(
            username="test_admin",
            password_hash="not-used-in-tests",
            full_name="Test Admin",
            role="Admin",
            email="admin@test.local",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        headers = _bearer(admin.user_id)

    with TestClient(app, headers=headers) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def anon_client(client):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session(client):
    with TestingSessionLocal() as db:
        yield db


@pytest.fixture
def auth_headers(db_session):
    counter = itertools.count(1)

    def _make(role: str = "Admin", is_active: bool = True) -> dict:
        n = next(counter)
        user = User(
            username=f"{role.lower()}_{n}",
            password_hash="not-used-in-tests",
            full_name=f"{role} {n}",
            role=role,
            is_active=is_active,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return _bearer(user.user_id)

    return _make


@pytest.fixture
def sample_category(client):
    return _create(client, "categories", {
        "category_name": "Beverages",
        "description": "Drinks and refreshments",
        "is_active": True,
    })


@pytest.fixture
def sample_supplier(client):
    return _create(client, "suppliers", {
        "supplier_name": "Coca-Cola Distributors",
        "contact_person": "John Smith",
        "phone": "+260971234567",
        "email": "john@cocacola.com",
        "address": "123 Industrial Road, Lusaka",
    })


@pytest.fixture
def sample_product(client, sample_category, sample_supplier):
    return _create(client, "products", {
        "sku": "CC001",
        "name": "Coca-Cola 500ml",
        "price": 12.50,
        "cost_price": 8.00,
        "quantity_in_stock": 100,
        "reorder_level": 20,
        "is_active": True,
        "category_id": sample_category["category_id"],
        "supplier_id": sample_supplier["supplier_id"],
    })


@pytest.fixture
def sample_user(client):
    return _create(client, "users", {
        "username": "cashier01",
        "password": "securepass123",
        "full_name": "Alice Banda",
        "role": "Cashier",
        "email": "alice@store.com",
        "is_active": True,
    })


@pytest.fixture
def sample_customer(client):
    return _create(client, "customers", {
        "first_name": "Chanda",
        "last_name": "Mulenga",
        "phone": "+260972345678",
        "email": "chanda@email.com",
        "loyalty_points": 0,
    })


@pytest.fixture
def make_sale(client, sample_customer, sample_user):
    def _make(**overrides) -> dict:
        payload = {
            "sale_date": "2026-08-01T10:30:00",
            "subtotal": 100.00,
            "tax_amount": 16.00,
            "discount_amount": 5.00,
            "total_amount": 111.00,
            "status": "Completed",
            "customer_id": sample_customer["customer_id"],
            "user_id": sample_user["user_id"],
        }
        payload.update(overrides)
        return _create(client, "sales", payload)

    return _make


@pytest.fixture
def sample_sale(make_sale):
    return make_sale()


@pytest.fixture
def sample_sale_item(client, sample_sale, sample_product):
    return _create(client, "sale-items", {
        "quantity": 2,
        "unit_price": 12.50,
        "discount": 0,
        "line_total": 25.00,
        "sale_id": sample_sale["sale_id"],
        "product_id": sample_product["product_id"],
    })


@pytest.fixture
def sample_payment(client, sample_sale):
    return _create(client, "payments", {
        "payment_method": "Cash",
        "amount": 60.00,
        "payment_date": "2026-08-01T10:35:00",
        "transaction_reference": None,
        "status": "Approved",
        "sale_id": sample_sale["sale_id"],
    })


@pytest.fixture
def sample_receipt(client, sample_sale):
    return _create(client, "receipts", {
        "receipt_number": "RCP-2026-0001",
        "issued_date": "2026-08-01T10:36:00",
        "file_url": "/receipts/RCP-2026-0001.pdf",
        "sale_id": sample_sale["sale_id"],
    })