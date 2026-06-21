from tests.fixtures.podcast import create_podcast_data


def test_get_all_podcasts(client, podcast):
    response = client.get("/podcasts/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == podcast.id
    assert data["items"][0]["title"] == podcast.title


def test_get_trending_podcasts(client, podcast):
    response = client.get("/podcasts/trending")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == podcast.id
    assert data[0]["title"] == podcast.title


def test_get_top_ranked_podcasts(client, podcast):
    response = client.get("/podcasts/top-charts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == podcast.id
    assert data[0]["title"] == podcast.title


def test_get_new_podcasts(client, podcast):
    response = client.get("/podcasts/new")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == podcast.id
    assert data[0]["title"] == podcast.title


def test_get_podcast_detail(client, podcast):
    response = client.get(f"/podcasts/{podcast.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == podcast.id
    assert data["title"] == podcast.title
    assert data["description"] == podcast.description
    assert data["audio_url"] == podcast.audio_url


def test_get_podcast_detail_not_found(client):
    response = client.get("/podcasts/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Podcast Not Found"


def test_get_podcast_stats(client, podcast):
    response = client.get(f"/podcasts/{podcast.id}/stats")
    assert response.status_code == 200
    body = response.json()
    assert "total_plays" in body
    assert "total_reviews" in body
    assert "average_rating" in body


def test_get_podcast_stats_not_found(client):
    response = client.get("/podcasts/99999/stats")
    assert response.status_code == 404


def test_get_podcast_subscribers(client, podcast):
    response = client.get(f"/podcasts/{podcast.id}/subscribers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_podcast_reviews(client, podcast):
    response = client.get(f"/podcasts/{podcast.id}/reviews")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body


def test_create_podcast(client, channel_auth_headers, audio_upload, image_upload):
    response = client.post(
        "/podcasts/",
        headers=channel_auth_headers["headers"],
        data={
            "title": "Python Podcast",
            "description": "Episode One",
            "duration": 120,
        },
        files={
            "audio_file": audio_upload,
            "image_file": image_upload,
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Python Podcast"
    assert data["description"] == "Episode One"
    assert data["duration"] == 120


def test_create_podcast_without_auth(client, audio_upload, image_upload):
    response = client.post(
        "/podcasts/",
        data={
            "title": "Python Podcast",
            "description": "Episode One",
            "duration": 120,
        },
        files={
            "audio_file": audio_upload,
            "image_file": image_upload,
        }
    )
    assert response.status_code == 401


def test_create_podcast_non_channel(client, authenticated_user, audio_upload, image_upload):
    response = client.post(
        "/podcasts/",
        headers={
            "Authorization": f"Bearer {authenticated_user['access_token']}"
        },
        data={
            "title": "Python Podcast",
            "description": "Episode One",
            "duration": 120,
        },
        files={
            "audio_file": audio_upload,
            "image_file": image_upload,
        }
    )
    assert response.status_code == 400
    assert (response.json()["detail"] ==
            "You are not allowed to create podcast")


def test_update_podcast(client, db_session, channel_auth_headers, audio_upload):
    podcast = create_podcast_data(channel_auth_headers["user"].id,)
    db_session.add(podcast)
    db_session.commit()
    db_session.refresh(podcast)
    response = client.put(
        f"/podcasts/{podcast.id}",
        headers=channel_auth_headers["headers"],
        data={
            "title": "Updated Podcast",
            "description": "Updated Description",
            "duration": 500,
        },
        files={
            "audio_file": audio_upload,
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Podcast"
    assert data["description"] == "Updated Description"
    assert data["duration"] == 500


def test_update_podcast_without_auth(client, db_session, channel_auth_headers):
    podcast = create_podcast_data(channel_auth_headers["user"].id)
    db_session.add(podcast)
    db_session.commit()
    db_session.refresh(podcast)
    response = client.put(
        f"/podcasts/{podcast.id}",
        data={
            "title": "Updated",
        }
    )
    assert response.status_code == 401


def test_update_podcast_not_found(client, channel_auth_headers, audio_upload):
    response = client.put(
        "/podcasts/9999",
        headers=channel_auth_headers["headers"],
        data={
            "title": "Updated",
        },
        files={
            "audio_file": audio_upload,
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Podcast not found"


def test_update_podcast_not_owner(client, podcast, authenticated_user, audio_upload):
    response = client.put(
        f"/podcasts/{podcast.id}",
        headers={
            "Authorization": (
                f"Bearer {authenticated_user['access_token']}"
            )
        },
        data={
            "title": "Hacked",
        },
        files={
            "audio_file": audio_upload,
        }
    )
    assert response.status_code == 403
    assert (response.json()["detail"] == "You are not the owner")


def test_update_podcast_title(client, db_session, channel_auth_headers):
    podcast = create_podcast_data(channel_auth_headers["user"].id)
    db_session.add(podcast)
    db_session.commit()
    db_session.refresh(podcast)
    response = client.put(
        f"/podcasts/{podcast.id}",
        headers=channel_auth_headers["headers"],
        data={
            "title": "Updated Title",
        }
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_update_podcast_duration(client, db_session, channel_auth_headers):
    podcast = create_podcast_data(channel_auth_headers["user"].id)
    db_session.add(podcast)
    db_session.commit()
    db_session.refresh(podcast)
    response = client.put(
        f"/podcasts/{podcast.id}",
        headers=channel_auth_headers["headers"],
        data={
            "duration": 999,
        }
    )
    assert response.status_code == 200
    assert response.json()["duration"] == 999


def test_update_podcast_not_found(client, channel_auth_headers):
    response = client.put(
        "/podcasts/99999",
        headers=channel_auth_headers["headers"],
        data={
            "title": "abc",
        }
    )
    assert response.status_code == 404


def test_delete_podcast(client, db_session, channel_auth_headers):
    podcast = create_podcast_data(channel_auth_headers["user"].id)
    db_session.add(podcast)
    db_session.commit()
    db_session.refresh(podcast)
    response = client.delete(
        f"/podcasts/{podcast.id}",
        headers=channel_auth_headers["headers"],
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Podcast deleted successfully"


def test_delete_podcast_without_auth(client, db_session, channel_auth_headers):
    podcast = create_podcast_data(channel_auth_headers["user"].id)
    db_session.add(podcast)
    db_session.commit()
    db_session.refresh(podcast)
    response = client.delete(f"/podcasts/{podcast.id}")
    assert response.status_code == 401


def test_delete_podcast_not_owner(client, db_session, channel_auth_headers, second_auth_headers):
    podcast = create_podcast_data(channel_auth_headers["user"].id)
    db_session.add(podcast)
    db_session.commit()
    db_session.refresh(podcast)
    response = client.delete(
        f"/podcasts/{podcast.id}",
        headers=second_auth_headers["headers"],
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "You are not the owner"


def test_delete_podcast_not_found(client, channel_auth_headers):
    response = client.delete(
        "/podcasts/999999",
        headers=channel_auth_headers["headers"],
    )
    assert response.status_code == 404
