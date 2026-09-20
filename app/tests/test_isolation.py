from sqlalchemy import text

import database
from config import settings

COLLECTIONS = [
    "categories", "suppliers", "products", "customers",
    "sales", "sale-items", "payments", "receipts",
]


def test_settings_point_at_sqlite():
    assert settings.DATABASE_URL == "sqlite://"


def test_application_engine_is_sqlite():
    assert database.engine.dialect.name == "sqlite"


def test_requests_are_served_from_a_sqlite_session(client, db_session):
    assert db_session.get_bind().dialect.name == "sqlite"
    assert database.get_db in client.app.dependency_overrides


def test_each_test_starts_with_an_empty_database(client):
    for collection in COLLECTIONS:
        assert client.get(f"/api/v1/{collection}/").json() == [], collection
    users = client.get("/api/v1/users/").json()
    assert [u["username"] for u in users] == ["test_admin"]


def test_sqlite_enforces_foreign_keys_like_postgres(db_session):
    assert db_session.execute(text("PRAGMA foreign_keys")).scalar() == 1
