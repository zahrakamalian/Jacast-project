import pytest
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.app import app
from src.data.database.database import Base, get_db
import src.data.models
from src.data.models.user import User, UserSession
from src.data.models.category import Category, CategoryPodcast
from src.data.models.podcast import Podcast
from tests.fixtures.users import create_user_data, create_login_data, create_channel_data
from tests.fixtures.podcast import create_podcast_data, create_audio_upload, create_image_upload
from tests.fixtures.playlist import create_playlist_data
from tests.fixtures.playlist import create_playlist_episode
from tests.fixtures.subscription import create_group, create_group_item, create_subscription


TEST_DATABASE_URL = "sqlite:///./test_jacast.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={
                       "check_same_thread": False})
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client, db_session):
    payload = create_user_data()
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 200
    db_user = (db_session.query(User).filter(
        User.email == payload["email"]).first())
    db_user.is_verified = True
    db_session.commit()
    return payload, response.json()


@pytest.fixture
def authenticated_user(client, db_session, registered_user):
    payload, _ = registered_user
    response = client.post(
        "/auth/login",
        data={
            "username": payload["email"],
            "password": payload["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    tokens = response.json()
    user = (db_session.query(User).filter(
        User.email == payload["email"]).first())
    session = (db_session.query(UserSession).filter(UserSession.user_id == user.id, UserSession.is_active.is_(True))
               .order_by(UserSession.id.desc()).first())
    return {
        "payload": payload,
        "user": user,
        "session": session,
        "session_id": session.id,
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"]
    }


@pytest.fixture
def second_user(client, db_session):
    payload = create_user_data()
    payload["is_channel"] = True
    response = client.post("/auth/register", json=payload,)
    assert response.status_code == 200
    user = (db_session.query(User).filter(
        User.email == payload["email"]).first())
    user.is_verified = True
    user.is_channel = True
    db_session.commit()
    return {
        "payload": payload,
        "user": user,
    }


@pytest.fixture
def channel(db_session):
    channel = create_channel_data()
    db_session.add(channel)
    db_session.commit()
    db_session.refresh(channel)
    return channel


@pytest.fixture
def podcast(db_session, channel):
    podcast = create_podcast_data(channel.id)
    db_session.add(podcast)
    db_session.commit()
    db_session.refresh(podcast)
    return podcast


@pytest.fixture
def category(db_session):
    category = Category(
        name="Technology",
        slug="technology",
        description="Technology podcasts",
        icon_url="/icons/technology.png",
        created_at=datetime.now(timezone.utc)
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def categories(db_session):
    result = []
    for i in range(5):
        category = Category(
            name=f"Category {i}",
            slug=f"category-{i}",
            description=f"description {i}",
            icon_url=f"/icons/{i}.png",
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(category)
        result.append(category)
    db_session.commit()
    for c in result:
        db_session.refresh(c)
    return result


@pytest.fixture
def category_with_podcast(db_session, category, podcast):
    relation = CategoryPodcast(
        category_id=category.id,
        podcast_id=podcast.id
    )
    db_session.add(relation)
    db_session.commit()
    return category


@pytest.fixture
def audio_upload():
    return create_audio_upload()


@pytest.fixture
def image_upload():
    return create_image_upload()


@pytest.fixture
def channel_auth_headers(client, db_session):
    payload = create_user_data()
    payload["is_channel"] = True
    register_response = client.post("/auth/register", json=payload,)
    assert register_response.status_code == 200
    user = (db_session.query(User).filter(
        User.email == payload["email"]).first())
    user.is_verified = True
    user.is_channel = True
    db_session.commit()
    login_response = client.post(
        "/auth/login",
        data={
            "username": payload["email"],
            "password": payload["password"],
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {
        "user": user,
        "headers": {
            "Authorization": f"Bearer {token}"
        }
    }


@pytest.fixture
def playlist(db_session, authenticated_user):
    playlist = create_playlist_data(authenticated_user["user"].id)
    db_session.add(playlist)
    db_session.commit()
    db_session.refresh(playlist)
    return playlist


@pytest.fixture
def private_playlist(db_session, authenticated_user):
    playlist = create_playlist_data(
        authenticated_user["user"].id, is_public=False)
    db_session.add(playlist)
    db_session.commit()
    db_session.refresh(playlist)
    return playlist


@pytest.fixture
def second_auth_headers(client, db_session, second_user):
    payload = second_user["payload"]
    login_response = client.post(
        "/auth/login",
        data={
            "username": payload["email"],
            "password": payload["password"],
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {
        "user": second_user["user"],
        "headers": {
            "Authorization": f"Bearer {token}"
        }
    }


@pytest.fixture
def playlist_episode(db_session, playlist, podcast):
    episode = create_playlist_episode(playlist.id, podcast.id)
    db_session.add(episode)
    db_session.commit()
    db_session.refresh(episode)
    return episode


@pytest.fixture
def second_playlist(db_session, authenticated_user):
    playlist = create_playlist_data(authenticated_user["user"].id)
    playlist.title = "Second Playlist"
    db_session.add(playlist)
    db_session.commit()
    db_session.refresh(playlist)
    return playlist


@pytest.fixture
def subscription(db_session, authenticated_user, channel):
    sub = create_subscription(authenticated_user["user"].id, channel.id)
    db_session.add(sub)
    db_session.commit()
    db_session.refresh(sub)
    return sub


@pytest.fixture
def second_channel(db_session):
    channel = create_channel_data("second_channel@test.com", "Second Channel")
    db_session.add(channel)
    db_session.commit()
    db_session.refresh(channel)
    return channel


@pytest.fixture
def subscription_group(db_session, authenticated_user):
    group = create_group(authenticated_user["user"].id)
    db_session.add(group)
    db_session.commit()
    db_session.refresh(group)
    return group


@pytest.fixture
def group_item(db_session, subscription_group, subscription):
    item = create_group_item(subscription_group.id, subscription.id)
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


@pytest.fixture
def normal_user(client, db_session):
    payload = create_user_data()
    payload["is_channel"] = False
    response = client.post("/auth/register",json=payload)
    assert response.status_code == 200
    user = (db_session.query(User).filter(User.email == payload["email"]).first())
    user.is_verified = True
    user.is_channel = False
    db_session.commit()
    return {
        "payload": payload,
        "user": user
    }
