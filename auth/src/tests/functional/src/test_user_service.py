import json

from auth.main import app
from auth.src.db.postgres import get_postgres_session
from auth.src.tests.functional.postgres import override_get_postgres_session
from fastapi.testclient import TestClient


app.dependency_overrides[get_postgres_session] = override_get_postgres_session

client = TestClient(app)


def test_register_user():
    response = client.post(
        "/api/v1/auth/user/register",
        json={"login": "superdev10", "email": "superdev10@example.com", "password": "chimichangas4life"},
    )
    data = response.json()
    assert data == "Вы успешно зарегистрировались."
    assert response.status_code == 201, response.text
