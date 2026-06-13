from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as sqlenum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from connections.database import Base


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    cover_art_url = Column(String)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="playlist")
    episodes = relationship(
        "PlaylistPodcast", back_populates="playlist", order_by="PlaylistPodcast.position")
    subscription = relationship(
        "SubscriptionPlaylist", back_populates="playlist")


class PlaylistPodcast(Base):
    __tablename__ = "playlist_podcast"

    id = Column(Integer, primary_key=True)
    podcast_id = Column(Integer, ForeignKey(
        "podcasts.id", ondelete="CASCADE"), nullable=False, index=True)
    playlist_id = Column(Integer, ForeignKey(
        "playlists.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(Integer, default=0)
    added_at = Column(DateTime, default=func.now())

    playlist = relationship("Playlist", back_populates="episodes")
    podcast = relationship("Podcast", back_populates="playlist")


class SubscriptionPlaylist(Base):
    __tablename__ = "subscription_playlist"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False, index=True)
    Playlist_id = Column(Integer, ForeignKey(
        "playlist.id", ondelete="CASCADE"), nullable=False, index=True)
    subscribed_at = Column(DateTime, default=func.now())

    subscriber = relationship("User", back_populates="subscribed_playlist")
    playlist = relationship("Playlist", back_populates="subscription")
