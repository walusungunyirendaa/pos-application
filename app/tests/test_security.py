from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

from config import settings
from services.auth_service import create_access_token, get_user_from_token


def _decode(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


class TestSecurity:
    def test_create_access_token(self):
        token = create_access_token({"sub": "1"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_user_id(self):
        payload = _decode(create_access_token({"sub": "42"}))
        assert payload["sub"] == "42"
        assert "exp" in payload

    def test_config_settings(self):
        assert settings.PROJECT_NAME == "POS System"
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30


class TestGetUserFromToken:
    def test_valid_token_returns_user(self, db_session, sample_user):
        token = create_access_token({"sub": str(sample_user["user_id"])})
        user = get_user_from_token(db_session, token)
        assert user.username == "cashier01"

    def test_garbage_token_rejected(self, db_session):
        with pytest.raises(HTTPException) as exc:
            get_user_from_token(db_session, "not-a-token")
        assert exc.value.status_code == 401

    def test_token_for_missing_user_rejected(self, db_session):
        token = create_access_token({"sub": "999999"})
        with pytest.raises(HTTPException) as exc:
            get_user_from_token(db_session, token)
        assert exc.value.status_code == 401


class TestTokenRejection:
    @pytest.mark.parametrize(
        "make_token",
        [
            lambda: create_access_token({"sub": "1"}, expires_delta=timedelta(seconds=-5)),
            lambda: jwt.encode({"sub": "1"}, "some-other-secret", algorithm="HS256"),
            lambda: create_access_token({"name": "no subject claim"}),
            lambda: create_access_token({"sub": "not-a-number"}),
            lambda: "",
            lambda: "a.b.c",
        ],
        ids=["expired", "wrong-secret", "no-sub", "non-numeric-sub", "empty", "malformed"],
    )
    def test_invalid_tokens_are_401(self, db_session, sample_user, make_token):
        with pytest.raises(HTTPException) as exc:
            get_user_from_token(db_session, make_token())
        assert exc.value.status_code == 401

    def test_bad_bearer_header_is_401_over_http(self, anon_client):
        response = anon_client.post(
            "/api/v1/categories/",
            json={"category_name": "X"},
            headers={"Authorization": "Bearer definitely.not.valid"},
        )
        assert response.status_code == 401

    def test_token_lifetime_matches_settings(self):
        payload = _decode(create_access_token({"sub": "1"}))
        lifetime = datetime.fromtimestamp(payload["exp"], timezone.utc) - datetime.now(timezone.utc)
        assert timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES - 1) < lifetime <= timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )


class TestRoleProtection:
    CATEGORY = {"category_name": "Snacks", "description": "x", "is_active": True}

    def test_unauthenticated_request_is_rejected(self, anon_client):
        response = anon_client.post("/api/v1/categories/", json=self.CATEGORY)
        assert response.status_code == 401

    def test_cashier_cannot_create_category(self, client, sample_user):
        token = create_access_token({"sub": str(sample_user["user_id"])})
        response = client.post(
            "/api/v1/categories/",
            json=self.CATEGORY,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    def test_admin_can_create_category(self, client):
        response = client.post("/api/v1/categories/", json=self.CATEGORY)
        assert response.status_code == 201