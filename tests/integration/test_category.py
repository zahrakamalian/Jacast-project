def test_get_all_categories(client, categories):
    response = client.get("/categories/")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 5
    assert body["page"] == 1
    assert len(body["items"]) == 5


def test_get_category_detail(client, category,):
    response = client.get(
        f"/categories/{category.id}"
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == category.id
    assert body["name"] == category.name


def test_get_unknown_category(client):
    response = client.get(
        "/categories/999999"
    )
    assert response.status_code == 404


def test_get_popular_categories(client, categories):
    response = client.get(
        "/categories/popular"
    )
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)


def test_get_category_not_found(client):
    response = client.get("/categories/999999")
    assert response.status_code == 404


def test_get_category_top_podcasts(client, category_with_podcast):
    response = client.get(
        f"/categories/{category_with_podcast.id}/top-podcasts"
    )
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["title"] == "Episode 1"


def test_get_top_podcast_invalid_category(client):
    response = client.get(
        "/categories/999999/top-podcasts"
    )
    assert response.status_code == 404


def test_get_category_trending_podcasts(client, category_with_podcast):
    response = client.get(
        f"/categories/{category_with_podcast.id}/trending"
    )
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["title"] == "Episode 1"


def test_get_trending_invalid_category(client):
    response = client.get(
        "/categories/999999/trending"
    )
    assert response.status_code == 404


def test_category_pagination(client):
    response = client.get(
        "/categories/?page=1&limit=5"
    )
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["limit"] == 5


def test_get_categories_pagination(client, categories):
    response = client.get(
        "/categories/?limit=2&page=2"
    )
    assert response.status_code == 200
    body = response.json()
    assert body["limit"] == 2
    assert body["page"] == 2
    assert len(body["items"]) == 2


def test_category_page_out_of_range(client, categories):
    response = client.get(
        "/categories/?page=100&limit=10"
    )
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []


def test_invalid_limit(client):
    response = client.get(
        "/categories/?limit=100"
    )
    assert response.status_code == 422


def test_invalid_page(client):
    response = client.get(
        "/categories/?page=0"
    )
    assert response.status_code == 422
