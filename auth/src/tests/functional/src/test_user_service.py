

from auth.src.tests.conftest import client





def test_register_user():
    response = client.post(
        "/api/v1/auth/user/register",
        json={
            "login": "superdev",
            "email": "superdev@example.com",
            "password": "chimichangas4life"
        },
    )
    data = response.json()
    assert data == "Вы успешно зарегистрировались."
    assert response.status_code == 201, response.text
