def test_get_subscriptions_empty(client, authenticated_user):
    response = client.get(
        "/subscriptions/",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_get_subscriptions(client, authenticated_user, subscription):
    response = client.get(
        "/subscriptions/",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1


def test_subscribe_channel(client, authenticated_user, channel):
    response = client.post(
        "/subscriptions/",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "channel_id": channel.id
        }
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == channel.id


def test_subscribe_channel_not_found(client, authenticated_user):
    response = client.post(
        "/subscriptions/",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "channel_id": 99999
        }
    )
    assert response.status_code == 404


def test_subscribe_channel_duplicate(client, authenticated_user, subscription):
    response = client.post(
        "/subscriptions/",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "channel_id": subscription.channel_id
        }
    )
    assert response.status_code == 400


def test_subscribe_non_channel(client, authenticated_user, normal_user):
    response = client.post(
        "/subscriptions/",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "channel_id": normal_user["user"].id
        }
    )
    assert response.status_code == 400


def test_subscribe_own_channel(client, channel_auth_headers):
    response = client.post(
        "/subscriptions/",
        headers=channel_auth_headers["headers"],
        json={
            "channel_id": channel_auth_headers["user"].id
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == (
        "You cannot subscribe to your own channel")


def test_unsubscribe_channel(client, authenticated_user, subscription):
    response = client.delete(
        f"/subscriptions/{subscription.channel_id}",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 200


def test_unsubscribe_not_subscribed(client, authenticated_user, channel):
    response = client.delete(
        f"/subscriptions/{channel.id}",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 400


def test_unsubscribe_channel_not_found(client, authenticated_user):
    response = client.delete(
        "/subscriptions/999999",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 404


def test_update_subscription(client, authenticated_user, subscription):
    response = client.patch(
        f"/subscriptions/{subscription.id}",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "notifications_enabled": False,
            "custom_name": "Backend Channel",
            "playback_speed": 1.5
        }
    )
    assert response.status_code == 200
    body = response.json()
    assert body["notifications_enabled"] is False
    assert body["custom_name"] == "Backend Channel"


def test_update_subscription_forbidden(client, subscription, second_auth_headers):
    response = client.patch(
        f"/subscriptions/{subscription.id}",
        headers=second_auth_headers["headers"],
        json={
            "custom_name": "Hack"
        }
    )
    assert response.status_code == 403


def test_update_subscription_not_found(client, authenticated_user):
    response = client.patch(
        "/subscriptions/999999",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "custom_name": "Backend"
        }
    )
    assert response.status_code == 404


def test_create_group(client, authenticated_user):
    response = client.post(
        "/subscriptions/groups",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "name": "Favorites"
        }
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Favorites"


def test_create_group_duplicate(client, authenticated_user, subscription_group):
    response = client.post(
        "/subscriptions/groups",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "name": subscription_group.name
        }
    )
    assert response.status_code == 400


def test_get_groups(client, authenticated_user, subscription_group):
    response = client.get(
        "/subscriptions/groups",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 200
    assert len(response.json()["groups"]) == 1


def test_update_group(client, authenticated_user, subscription_group):
    response = client.put(
        f"/subscriptions/groups/{subscription_group.id}",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "name": "Updated Group"
        }
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Group"


def test_update_group_not_found(client, authenticated_user):
    response = client.put(
        "/subscriptions/groups/999999",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "name": "Updated"
        }
    )
    assert response.status_code == 404


def test_update_group_forbidden(client, subscription_group, second_auth_headers):
    response = client.put(
        f"/subscriptions/groups/{subscription_group.id}",
        headers=second_auth_headers["headers"],
        json={
            "name": "Hack"
        }
    )
    assert response.status_code == 403


def test_delete_group(client, authenticated_user, subscription_group):
    response = client.delete(
        f"/subscriptions/groups/{subscription_group.id}",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 200


def test_delete_group_forbidden(client, subscription_group, second_auth_headers):
    response = client.delete(
        f"/subscriptions/groups/{subscription_group.id}",
        headers=second_auth_headers["headers"]
    )
    assert response.status_code == 403


def test_delete_group_not_found(client, authenticated_user):
    response = client.delete(
        "/subscriptions/groups/999999",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 404


def test_add_subscription_to_group(client, authenticated_user, subscription_group, subscription):
    response = client.post(
        f"/subscriptions/groups/{subscription_group.id}/subscriptions/{subscription.id}",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 201
    body = response.json()
    assert len(body["subscriptions"]) == 1


def test_add_subscription_to_group_duplicate(client, authenticated_user, subscription_group, group_item, subscription):
    response = client.post(
        f"/subscriptions/groups/{subscription_group.id}/subscriptions/{subscription.id}",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 400


def test_add_subscription_to_group_subscription_not_found(client, authenticated_user, subscription_group):
    response = client.post(
        f"/subscriptions/groups/{subscription_group.id}/subscriptions/999999",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 404


def test_add_subscription_to_group_forbidden(client, subscription_group, subscription, second_auth_headers):
    response = client.post(
        f"/subscriptions/groups/{subscription_group.id}/subscriptions/{subscription.id}",
        headers=second_auth_headers["headers"]
    )
    assert response.status_code == 403


def test_remove_subscription_from_group(client, authenticated_user, subscription_group, group_item, subscription):
    response = client.delete(
        f"/subscriptions/groups/{subscription_group.id}/subscriptions/{subscription.id}",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 200


def test_remove_subscription_not_in_group(client, authenticated_user, subscription_group, subscription):
    response = client.delete(
        f"/subscriptions/groups/{subscription_group.id}/subscriptions/{subscription.id}",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 400


def test_remove_subscription_from_group_forbidden(client, subscription_group, subscription, second_auth_headers):
    response = client.delete(
        f"/subscriptions/groups/{subscription_group.id}/subscriptions/{subscription.id}",
        headers=second_auth_headers["headers"]
    )
    assert response.status_code == 403
