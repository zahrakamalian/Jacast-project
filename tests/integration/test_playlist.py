from tests.fixtures.playlist import create_playlist_data


def test_get_user_playlists_empty(client, authenticated_user):
    response = client.get(
        "/playlists/",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
    )
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_get_user_playlists(client, authenticated_user, playlist):
    response = client.get(
        "/playlists/",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["title"] == playlist.title


def test_get_user_playlists_only_owner_items(client, second_auth_headers):
    response = client.get(
        "/playlists/",
        headers=second_auth_headers["headers"]
    )
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_get_playlist_detail(client, playlist):
    response = client.get(f"/playlists/{playlist.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == playlist.id
    assert body["title"] == playlist.title


def test_get_playlist_detail_not_found(client):
    response = client.get("/playlists/999999")
    assert response.status_code == 404


def test_get_private_playlist_without_owner(client, private_playlist):
    response = client.get(f"/playlists/{private_playlist.id}")
    assert response.status_code == 403


def test_get_private_playlist_without_auth(client, private_playlist):
    response = client.get(f"/playlists/{private_playlist.id}")
    assert response.status_code == 403


def test_get_private_playlist_other_user(client, private_playlist, second_auth_headers):
    response = client.get(
        f"/playlists/{private_playlist.id}",
        headers=second_auth_headers["headers"]
    )
    assert response.status_code == 403


def test_create_playlist(client, authenticated_user):
    response = client.post(
        "/playlists/",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "title": "Python",
            "description": "Backend",
            "is_public": True,
        }
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Python"
    assert body["description"] == "Backend"


def test_create_playlist_duplicate(client, authenticated_user, playlist):
    response = client.post(
        "/playlists/",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "title": playlist.title,
        }
    )
    assert response.status_code == 400


def test_create_playlist_invalid_title(client, authenticated_user):
    response = client.post(
        "/playlists/",
        json={
            "title": ""
        },
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 422


def test_update_playlist(client, authenticated_user, playlist):
    response = client.put(
        f"/playlists/{playlist.id}",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        },
        json={
            "title": "Updated Playlist"
        }
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Playlist"


def test_update_playlist_not_owner(client, playlist, second_auth_headers):
    response = client.put(
        f"/playlists/{playlist.id}",
        headers=second_auth_headers["headers"],
        json={
            "title": "Hack"
        },
    )
    assert response.status_code == 403


def test_update_playlist_not_found(client, authenticated_user):
    response = client.put(
        "/playlists/9999",
        json={
            "title": "Updated Playlist"
        },
        headers={
            "Authorization": f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Playlist not found"


def test_update_playlist_forbidden(client, playlist, second_auth_headers):
    response = client.put(
        f"/playlists/{playlist.id}",
        json={
            "title": "Hacked Playlist"
        },
        headers=second_auth_headers["headers"]
    )
    assert response.status_code == 403


def test_update_playlist_empty_payload(client, playlist, authenticated_user):
    response = client.put(
        f"/playlists/{playlist.id}",
        json={},
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code in [200, 400]


def test_delete_playlist(client, authenticated_user, playlist):
    response = client.delete(
        f"/playlists/{playlist.id}",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == ("Playlist deleted successfully")


def test_delete_playlist_not_found(client, authenticated_user):
    response = client.delete(
        "/playlists/9999",
        headers={
            "Authorization": f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 404


def test_delete_playlist_forbidden(client, playlist, second_auth_headers):
    response = client.delete(
        f"/playlists/{playlist.id}",
        headers=second_auth_headers["headers"]
    )
    assert response.status_code == 403


def test_get_user_playlists_pagination(client, db_session, authenticated_user,):
    for i in range(15):
        playlist = create_playlist_data(authenticated_user["user"].id)
        playlist.title = f"Playlist {i}"
        db_session.add(playlist)
    db_session.commit()

    response = client.get(
        "/playlists/?page=2&limit=10",
        headers={
            "Authorization": f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert len(data["items"]) == 5
    assert data["has_prev"] is True


def test_get_user_playlists_page_out_of_range(client, authenticated_user):
    response = client.get(
        "/playlists/?page=999&limit=10",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []


def test_get_public_playlists_only_public(client, playlist, private_playlist):
    response = client.get("/playlists/public/playlists")
    assert response.status_code == 200
    data = response.json()
    ids = [item["id"] for item in data["items"]]
    assert playlist.id in ids
    assert private_playlist.id not in ids


def test_add_episode_success(client, playlist, podcast, authenticated_user):
    response = client.post(
        f"/playlists/{playlist.id}/episodes",
        json={
            "podcast_id": podcast.id
        },
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 201
    body = response.json()
    assert body["podcast_id"] == podcast.id


def test_add_episode_duplicate(client, playlist, podcast, authenticated_user):
    client.post(
        f"/playlists/{playlist.id}/episodes",
        json={
            "podcast_id": podcast.id
        },
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    response = client.post(
        f"/playlists/{playlist.id}/episodes",
        json={
            "podcast_id": podcast.id
        },
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 400


def test_add_episode_playlist_not_found(client, podcast, authenticated_user):
    response = client.post(
        "/playlists/9999/episodes",
        json={
            "podcast_id": podcast.id
        },
        headers={
            "Authorization": f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 404


def test_add_episode_podcast_not_found(client, playlist, authenticated_user):
    response = client.post(
        f"/playlists/{playlist.id}/episodes",
        json={
            "podcast_id": 9999
        },
        headers={
            "Authorization": f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 404


def test_add_episode_forbidden(client, playlist, podcast, second_auth_headers):
    response = client.post(
        f"/playlists/{playlist.id}/episodes",
        json={
            "podcast_id": podcast.id
        },
        headers=second_auth_headers["headers"]
    )
    assert response.status_code == 403


def test_remove_episode_success(client, playlist, playlist_episode, authenticated_user):
    response = client.delete(
        f"/playlists/{playlist.id}/episodes/{playlist_episode.id}",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 200


def test_remove_episode_not_found(client, playlist, authenticated_user):
    response = client.delete(
        f"/playlists/{playlist.id}/episodes/9999",
        headers={
            "Authorization": f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 404


def test_remove_episode_forbidden(client, playlist, playlist_episode, second_auth_headers):
    response = client.delete(
        f"/playlists/{playlist.id}/episodes/{playlist_episode.id}",
        headers=second_auth_headers["headers"]
    )
    assert response.status_code == 403


def test_remove_episode_from_wrong_playlist(client, second_playlist, playlist_episode, authenticated_user):
    response = client.delete(
        f"/playlists/{second_playlist.id}/episodes/{playlist_episode.id}",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 400


def test_owner_can_view_private_playlist(client, private_playlist, authenticated_user):
    response = client.get(
        f"/playlists/{private_playlist.id}",
        headers={
            "Authorization":
                f"Bearer {authenticated_user['access_token']}"
        }
    )
    assert response.status_code == 200
