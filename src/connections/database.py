import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi import Depends
from typing import Annotated

from config import settings


if os.getenv("RENDER"):
    DB_PATH = "/tmp/jacast.db"
    DATABASE_URL = f"sqlite:///{DB_PATH}"
else:
    DATABASE_URL = settings.DATABASE_URL


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
