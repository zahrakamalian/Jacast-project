def test_search_all_empty_result(client):
    response = client.get("/search/?q=zzzzzzzzzz")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0


def test_search_all_podcasts(client, podcast):
    response = client.get(f"/search/?q={podcast.title}")
    assert response.status_code == 200
    body = response.json()
    assert body["podcasts"]["total"] >= 1


def test_search_all_users(client, channel):
    response = client.get(f"/search/?q={channel.display_name}")
    assert response.status_code == 200
    body = response.json()
    assert body["users"]["total"] >= 1


def test_search_all_playlists(client, playlist):
    response = client.get(f"/search/?q={playlist.title}")
    assert response.status_code == 200
    body = response.json()
    assert body["playlists"]["total"] >= 1


def test_search_podcasts(client, podcast):
    response = client.get(f"/search/podcasts?q={podcast.title}")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1


def test_search_podcasts_empty(client):
    response = client.get("/search/podcasts?q=zzzzzzzzzz")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_search_episodes(client, podcast):
    response = client.get("/search/episodes", params={"q": podcast.title})
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_search_episodes_empty(client):
    response = client.get("/search/episodes?q=zzzzzzzzzz")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_search_users(client, channel):
    response = client.get(f"/search/users?q={channel.display_name}")
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_search_users_empty(client):
    response = client.get("/search/users?q=zzzzzzzzzz")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_search_playlists(client, playlist):
    response = client.get(f"/search/playlists?q={playlist.title}")
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_search_playlists_empty(client):
    response = client.get("/search/playlists?q=zzzzzzzzzz")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_search_query_too_short(client):
    response = client.get("/search/?q=a")
    assert response.status_code == 422


def test_search_invalid_type(client):
    response = client.get("/search/?q=test&type=invalid")
    assert response.status_code == 422


def test_browse(client):
    response = client.get("/discover/browse")
    assert response.status_code == 200
    body = response.json()
    assert "new_releases" in body
    assert "trending" in body
    assert "popular" in body
    assert "categories" in body


def test_get_categories(client):
    response = client.get("/discover/categories")
    assert response.status_code == 200


def test_get_category_detail(client, category):
    response = client.get(f"/discover/categories/{category.id}")
    assert response.status_code == 200
    assert response.json()["id"] == category.id


def test_get_category_detail_not_found(client):
    response = client.get("/discover/categories/99999")
    assert response.status_code == 404


def test_get_category_podcasts(client, category_with_podcast):
    response = client.get(
        f"/discover/categories/{category_with_podcast.id}/podcasts")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1


def test_get_category_podcasts_not_found(client):
    response = client.get("/discover/categories/99999/podcasts")
    assert response.status_code == 404


def test_get_trending(client):
    response = client.get("/discover/trending")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_popular(client):
    response = client.get("/discover/popular")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_podcasts_pagination(client, podcast):
    response = client.get(f"/search/podcasts?q={podcast.title}&page=1&limit=1")
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["limit"] == 1
