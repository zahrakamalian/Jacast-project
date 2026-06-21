# Jacast API

**Jacast** is a modern podcast streaming platform backend built with **FastAPI**. This RESTful API provides comprehensive features including secure authentication, podcast management, playlists, subscriptions, search & discovery, and user profiles.

## Features

### Authentication & Security
- User registration and login
- JWT access and refresh tokens
- Email verification
- Password reset flow
- Two-factor authentication (2FA) using PyOTP

### Users
- User profile management
- Avatar upload
- Channel accounts
- User search
- Follow/unfollow system

### Podcasts
- Create, update and delete podcasts
- Podcast discovery
- Trending and popular podcasts

### Playlists
- Create, update and delete playlists
- Public and private playlists
- Playlist subscriptions
- Playlist collaboration

### Subscriptions
- Subscribe / unsubscribe from channels
- Custom subscription settings
- Subscription groups

### Search & Discovery
- Global search
- Podcast, episode, user and playlist search
- Browse page, Trending section and Categories

### Categories
- Category listing and details
- Podcasts in each category

## Tech Stack

- **FastAPI**
- **SQLAlchemy** + SQLite (for development) / PostgreSQL (recommended for production)
- **Alembic** (Database Migrations)
- **Pydantic v2**
- **JWT Authentication**
- **PyOTP** (2FA)
- **Pytest** (Testing)

## Project Structure

```text
.
├── src/
│   ├── api/
│   │   └── v1/              # Routers (API endpoints)
│   ├── services/            # Business logic
│   ├── repository/          # Database operations
│   ├── schemas/             # Pydantic models
│   ├── data/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── database/        # Database connection & engine
│   │   └── alembic/         # Migration scripts
│   ├── config.py            # Settings & configuration
│   └── app.py               # FastAPI application
├── tests/
│   ├── fixtures/
│   └── integration/
├── resources/               # Uploaded files (avatars, audio, covers)
├── .env.example
├── requirements.txt
├── alembic.ini
├── Dockerfile
└── railpack.json            # Railway deployment config
```

##Installation & Quick Start (Local)
1. Clone the Repository

```
git clone https://github.com/zahrakamalian/Jacast-project.git
cd Jacast-project
```
2. Create Virtual Environment
```
python -m venv env

# Linux / macOS
source env/bin/activate

# Windows
env\Scripts\activate
```
3. Install Dependencies
```
pip install -r requirements.txt
```
4. Configure Environment Variables
```
cp .env.example .env
```
Edit the .env file and set the important values (especially SECRET_KEY).
5. Run the Application
```
uvicorn src.app:app --reload
```
URLs:

- Application: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Running Tests
```
# Regular tests
pytest

# Tests with coverage
pytest --cov=src
```
## Deployment
Docker (Local or Any Server)
```
docker build -t jacast-api .

docker run -p 8000:8000 \
  -v $(pwd)/jacast.db:/app/jacast.db \
  -v $(pwd)/resources:/app/resources \
  jacast-api
```
## Current Status (MVP)
Implemented:

- Authentication + 2FA
- Users & Profiles
- Podcasts
- Playlists
- Subscriptions
- Search & Discovery
- Categories

Planned for future:

- PostgreSQL support
- Redis caching
- Background jobs (Celery)
- Recommendation system
- Full CI/CD pipeline
- Production optimizations (S3 storage, etc.)

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.