from enum import Enum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as sqlenum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from connections.database import Base


class Permissions(str, Enum):
    ADD = "add"
    EDIT = "edit"
    ADMIN = "admin"


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
    is_collaborative = Column(Boolean, default=False)

    user = relationship("User", back_populates="playlist")
    episodes = relationship(
        "PlaylistPodcast", back_populates="playlist", order_by="PlaylistPodcast.position")
    subscription = relationship(
        "SubscriptionPlaylist", back_populates="playlist")
    shares = relationship("PlaylistShare", back_populates="playlist")
    collaborators = relationship(
        "PlaylistCollaborator", back_populates="playlist")


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
    playlist_id = Column(Integer, ForeignKey(
        "playlists.id", ondelete="CASCADE"), nullable=False, index=True)
    subscribed_at = Column(DateTime, default=func.now())

    subscriber = relationship("User", back_populates="subscribed_playlist")
    playlist = relationship("Playlist", back_populates="subscription")


class PlaylistShare(Base):
    __tablename__ = "playlist_shares"

    id = Column(Integer, primary_key=True)
    playlist_id = Column(Integer, ForeignKey(
        "playlists.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    click_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())

    playlist = relationship("Playlist", back_populates="shares")


class PlaylistCollaborator(Base):
    __tablename__ = "playlist_collaborators"

    id = Column(Integer, primary_key=True)
    playlist_id = Column(Integer, ForeignKey(
        "playlists.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False, index=True)
    permission = Column(sqlenum(Permissions), default=Permissions.EDIT)
    added_at = Column(DateTime, default=func.now())

    playlist = relationship("Playlist", back_populates="collaborators")
    user = relationship("User", back_populates="playlist_collaborations")
