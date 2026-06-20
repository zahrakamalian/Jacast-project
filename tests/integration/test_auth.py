from tests.fixtures.users import create_user_data, create_login_data


def test_register_success(client):
    payload = create_user_data()
    response = client.post(
        "/auth/register",
        json=payload
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["display_name"] == payload["display_name"]
    assert "id" in data


def test_register_duplicate_email(client):
    payload = create_user_data()
    response1 = client.post(
        "/auth/register",
        json=payload
    )
    assert response1.status_code == 200
    response2 = client.post(
        "/auth/register",
        json=payload,
    )
    assert response2.status_code == 400


def test_login_success(client, registered_user):
    payload, _ = registered_user
    response = client.post(
        "/auth/login",
        data=create_login_data(
            payload["email"],
            payload["password"]
        )
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    payload, _ = registered_user
    response = client.post(
        "/auth/login",
        data=create_login_data(
            payload["email"],
            "WrongPassword123!"
        )
    )
    assert response.status_code == 401


def test_refresh_token_success(client, authenticated_user):
    response = client.post(
        "/auth/refresh-token",
        json={
            "token": authenticated_user["refresh_token"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_token_invalid(client):
    response = client.post(
        "/auth/refresh-token",
        json={
            "token": "invalid-token"
        }
    )
    assert response.status_code == 401


def test_forgot_password_existing_email(client, registered_user):
    payload, _ = registered_user
    response = client.post(
        "/auth/forgot-password",
        json={
            "email": payload["email"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data


def test_forgot_password_unknown_email(client):
    response = client.post(
        "/auth/forgot-password",
        json={
            "email": "unknown@example.com"
        }
    )
    assert response.status_code == 200


def test_logout_success(client, authenticated_user,):
    token = authenticated_user["access_token"]
    response = client.post(
        "/auth/logout",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200


def test_get_active_sessions(client, authenticated_user,):
    token = authenticated_user["access_token"]
    response = client.get(
        "/auth/sessions",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delete_session_success(client, authenticated_user):
    response = client.delete(
        f"/auth/sessions/{authenticated_user['session_id']}",
        headers={
            "Authorization": f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "Session deactivated successfully"
    }


def test_delete_non_existing_session(client, authenticated_user):
    response = client.delete(
        "/auth/sessions/999999",
        headers={
            "Authorization": f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 404
