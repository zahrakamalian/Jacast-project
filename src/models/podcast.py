from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as sqlenum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from connections.database import Base


class ReportReason(str, Enum):
    SPAM = "spam"
    HARASSMENT = "harassment"
    HATE_SPEECH = "hate_speech"
    COPYRIGHT = "copyright"
    ADULT_CONTENT = "adult_content"
    OTHER = "other"


class ReportStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    DISMISSED = "dismissed"


class Podcast(Base):
    __tablename__ = "podcasts"

    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    cover_art_url = Column(String)
    audio_url = Column(String, nullable=False)
    duration = Column(Integer, nullable=True)
    play_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

    channel = relationship("User", back_populates="podcasts")
    reviews = relationship("Review", back_populates="podcast")
    reports = relationship("Report", back_populates="podcast")
    sharelink = relationship("ShareLink", back_populates="podcast")
    playlist = relationship("PlaylistPodcast", back_populates="podcast")
    categories = relationship("CategoryPodcast", back_populates="podcast")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    podcast_id = Column(Integer, ForeignKey(
        "podcasts.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, nullable=True)

    author = relationship("User", back_populates="reviews")
    podcast = relationship("Podcast", back_populates="reviews")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    podcast_id = Column(Integer, ForeignKey(
        "podcasts.id", ondelete="CASCADE"), nullable=False)
    reason = Column(sqlenum(ReportReason), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(sqlenum(ReportStatus), default=ReportStatus.PENDING)
    created_at = Column(DateTime, default=func.now())

    reporter = relationship("User", back_populates="reports")
    podcast = relationship("Podcast", back_populates="reports")


class ShareLink(Base):
    __tablename__ = "sharelinks"

    id = Column(Integer, primary_key=True)
    podcast_id = Column(Integer, ForeignKey(
        "podcasts.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, index=True)
    click_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

    podcast = relationship("Podcast", back_populates="sharelink")
