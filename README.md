# Jacast API

A modern podcast streaming platform API built with **FastAPI**. Features include JWT authentication, email verification, password reset, two-factor authentication (2FA), user profiles, follow/unfollow system, and more.

## Tech Stack

- FastAPI
- SQLAlchemy + SQLite
- JWT Authentication
- 2FA (PyOTP)

## Features

- User registration & login
- JWT access/refresh tokens
- Email verification
- Password reset
- Two-factor authentication
- Profile management
- Follow/unfollow users

## Quick Start

```bash
# Clone
git clone https://github.com/yourusername/Jacast-project.git
cd Jacast-project

# Setup
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your SECRET_KEY

# Run
cd src
uvicorn app:app --reload 
```

## API Docs
After running: http://localhost:8000/swagger

## Project Structure
```
src/
├── api/           # Routes
├── services/      # Business logic
├── repository/    # DB operations
├── models/        # SQLAlchemy models
├── schemas/       # Pydantic schemas
├──connections/   # Database connection
├── config.py # Application settings
└── app.py # FastAPI application
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request.