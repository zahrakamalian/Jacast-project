import uuid
from tests.fixtures.users import create_user_data, create_login_data


def test_get_me(client, authenticated_user):
    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 200
    assert response.json()["email"] == authenticated_user["payload"]["email"]


def test_update_profile(client, authenticated_user):
    response = client.patch(
        "/users/me",
        headers={
            "Authorization": f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "display_name": "new_name",
            "bio": "hello world"
        }
    )
    assert response.status_code == 200
    body = response.json()
    assert body["display_name"] == "new_name"
    assert body["bio"] == "hello world"


def test_change_password(client, authenticated_user):
    response = client.patch(
        "/users/me/password",
        headers={
            "Authorization": f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "current_password": authenticated_user["payload"]["password"],
            "new_password": "MyNewPassword123",
            "confirm_password": "MyNewPassword123"
        }
    )
    assert response.status_code == 200


def test_change_password_wrong_current_password(client, authenticated_user,):
    response = client.patch(
        "/users/me/password",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "current_password": "WrongPassword",
            "new_password": "NewPassword123",
            "confirm_password": "NewPassword123"
        }
    )
    assert response.status_code == 401


def test_change_password_confirm_mismatch(client, authenticated_user):
    response = client.patch(
        "/users/me/password",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "current_password": authenticated_user["payload"]["password"],
            "new_password": "NewPassword123",
            "confirm_password": "AnotherPassword"
        }
    )
    assert response.status_code == 400


def test_change_password_same_as_old(client, authenticated_user):
    old_password = authenticated_user["payload"]["password"]
    response = client.patch(
        "/users/me/password",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "current_password": old_password,
            "new_password": old_password,
            "confirm_password": old_password
        }
    )
    assert response.status_code == 400


def test_change_email(client, authenticated_user):
    new_email = f"{uuid.uuid4().hex}@example.com"
    response = client.patch(
        "/users/me/email",
        headers={
            "Authorization": f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "email": authenticated_user["payload"]["email"],
            "new_email": new_email
        }
    )
    assert response.status_code == 200


def test_change_email_wrong_current_email(client, authenticated_user):
    response = client.patch(
        "/users/me/email",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "email": "wrong@example.com",
            "new_email": f"{uuid.uuid4().hex}@example.com",
        }
    )
    assert response.status_code == 401


def test_change_email_same_email(client, authenticated_user):
    email = authenticated_user["payload"]["email"]
    response = client.patch(
        "/users/me/email",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "email": email,
            "new_email": email
        }
    )
    assert response.status_code == 400


def test_change_email_duplicate(client, authenticated_user, second_user):
    response = client.patch(
        "/users/me/email",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "email":
                authenticated_user["payload"]["email"],
            "new_email":
                second_user["payload"]["email"]
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Email already exists"
    )


def test_public_profile(client, authenticated_user):
    user_id = authenticated_user["user"].id
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_public_profile_not_found(client):
    response = client.get("/users/999999")
    assert response.status_code == 404


def test_follow_user_success(client, authenticated_user, second_user):
    response = client.post(
        f"/users/{second_user['user'].id}/follow",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "Successfully followed"
    }


def test_follow_duplicate(client, authenticated_user, second_user):
    client.post(
        f"/users/{second_user['user'].id}/follow",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    response = client.post(
        f"/users/{second_user['user'].id}/follow",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 400


def test_follow_self(client, authenticated_user):
    response = client.post(
        f"/users/{authenticated_user['user'].id}/follow",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 400


def test_follow_non_existing_user(client, authenticated_user):
    response = client.post(
        "/users/999999/follow",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 404


def test_unfollow_success(client, authenticated_user, second_user):
    client.post(
        f"/users/{second_user['user'].id}/follow",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    response = client.delete(
        f"/users/{second_user['user'].id}/unfollow",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "Successfully Unfollowed!"
    }


def test_unfollow_without_follow(client, authenticated_user, second_user):
    response = client.delete(
        f"/users/{second_user['user'].id}/unfollow",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 400


def test_get_followers(
        client,
        authenticated_user,
        second_user,):
    client.post(
        f"/users/{second_user['user'].id}/follow",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
    )

    response = client.get(
        f"/users/{second_user['user'].id}/followers"
    )

    assert response.status_code == 200

    followers = response.json()

    assert len(followers) == 1

    assert (
        followers[0]["email"]
        == authenticated_user["payload"]["email"]
    )


def test_get_following(
        client,
        authenticated_user,
        second_user,):
    client.post(
        f"/users/{second_user['user'].id}/follow",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
    )

    response = client.get(
        f"/users/{authenticated_user['user'].id}/following"
    )

    assert response.status_code == 200

    following = response.json()

    assert len(following) == 1

    assert (
        following[0]["email"]
        == second_user["payload"]["email"]
    )


def test_delete_user_success(
        client,
        authenticated_user,):
    response = client.delete(
        "/users/me",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "message": "Deleted User Successfully"
    }


def test_delete_user_really_deleted(
        client,
        authenticated_user,):
    token = authenticated_user["access_token"]

    response = client.delete(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    response = client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code in (
        401,
        404,
    )
 