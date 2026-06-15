from datetime import datetime, timezone

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from config import settings
from models.playlist import Playlist, PlaylistPodcast, SubscriptionPlaylist, PlaylistShare, PlaylistCollaborator
from models.user import User
from models.podcast import Podcast
from schemas.playlist import PlaylistResponse


class PlaylistRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_playlists(self, user_id: int, offset: int, limit: int) -> List[Playlist]:
        return self.db.query(Playlist).options(joinedload(Playlist.episodes)).filter(Playlist.user_id == user_id).order_by(Playlist.created_at.desc()).offset(offset).limit(limit).all()

    def count_user_playlists(self, user_id: int) -> int:
        return self.db.query(Playlist).filter(Playlist.user_id == user_id).count()

    def get_playlist_by_id(self, playlist_id) -> Playlist | None:
        return self.db.query(Playlist).options(joinedload(Playlist.user), joinedload(Playlist.episodes).joinedload(PlaylistPodcast.podcast).joinedload(Podcast.channel)).filter(Playlist.id == playlist_id).first()

    def get_playlist_by_user_and_title(self, user_id: int, title: str) -> Playlist | None:
        return self.db.query(Playlist).filter(Playlist.user_id == user_id, Playlist.title == title).first()

    def count_playlist_episodes(self, playlist_id: int) -> int:
        return self.db.query(PlaylistPodcast).filter(PlaylistPodcast.playlist_id == playlist_id).count()

    def create_playlist(self, playlist: Playlist) -> Playlist:
        self.db.add(playlist)
        self.db.commit()
        self.db.refresh(playlist)
        return playlist

    def update_playlist(self, playlist: Playlist, title: Optional[str], description: Optional[str], is_public: Optional[bool], cover_art_url: Optional[str] = None) -> Playlist:
        if title is not None and title != playlist.title:
            playlist.title = title
        if description is not None and description != playlist.description:
            playlist.description = description
        if is_public is not None and is_public != playlist.is_public:
            playlist.is_public = is_public
        if cover_art_url is not None and cover_art_url != playlist.cover_art_url:
            playlist.cover_art_url = cover_art_url

        self.db.commit()
        self.db.refresh(playlist)
        return playlist

    def delete_playlist_cover_file(self, cover_url: str) -> None:
        if cover_url:
            file_name = cover_url.split('/')[-1]
            file_path = settings.PLAYLIST_COVER_DIR / file_name
            if file_path.exists():
                file_path.unlink()

    def update_cover_art_url(self, playlist: Playlist, cover_art_url: str) -> Playlist:
        if cover_art_url and cover_art_url != playlist.cover_art_url:
            playlist.cover_art_url = cover_art_url
            self.db.commit()
            self.db.refresh(playlist)

        return playlist

    def delete_playlist(self, playlist: Playlist) -> None:
        self.db.delete(playlist)
        self.db.commit()

    def update_playlist_cover(self, playlist: Playlist, cover_url: str) -> Playlist:
        playlist.cover_art_url = cover_url
        self.db.commit()
        self.db.refresh(playlist)
        return playlist

    def get_playlist_episode(self, playlist_id: int, podcast_id: int) -> PlaylistPodcast | None:
        return self.db.query(PlaylistPodcast).filter(PlaylistPodcast.playlist_id == playlist_id, PlaylistPodcast.podcast_id == podcast_id).first()

    def get_last_position_in_playlist(self, playlist_id: int) -> int:
        result = self.db.query(func.max(PlaylistPodcast.position)).filter(
            PlaylistPodcast.playlist_id == playlist_id).scalar()
        return (result + 1) if result is not None else 0

    def add_episode_to_playlist(self, episode: PlaylistPodcast) -> PlaylistPodcast:
        self.db.add(episode)
        self.db.commit()
        self.db.refresh(episode)
        return episode

    def get_playlist_episode_by_id(self, episode_id: int) -> PlaylistPodcast | None:
        return self.db.query(PlaylistPodcast).filter(PlaylistPodcast.id == episode_id).first()

    def delete_playlist_episode(self, episode: PlaylistPodcast) -> None:
        self.db.delete(episode)
        self.db.commit()

    def reorder_positions_after_deletion(self, playlist_id: int, deleted_position: int) -> None:
        episodes = self.db.query(PlaylistPodcast).filter(
            PlaylistPodcast.playlist_id == playlist_id, PlaylistPodcast.position > deleted_position).all()
        for episode in episodes:
            episode.position -= 1
        self.db.commit()

    def get_all_episodes_by_playlist_id(self, playlist_id: int) -> List[PlaylistPodcast]:
        return self.db.query(PlaylistPodcast).filter(PlaylistPodcast.playlist_id == playlist_id).all()

    def bulk_update_episode_positions(self, updates: list[tuple[int, int]]) -> None:
        for episode_id, new_position in updates:
            self.db.query(PlaylistPodcast).filter(
                PlaylistPodcast.id == episode_id).update({"position": new_position})
        self.db.commit()

    def get_existing_episode_ids(self, playlist_id: int) -> set[int]:
        result = self.db.query(PlaylistPodcast.podcast_id).filter(
            PlaylistPodcast.playlist_id == playlist_id).all()
        return {row[0] for row in result}

    def bulk_add_episodes(self, episodes: List[PlaylistPodcast]) -> None:
        self.db.add_all(episodes)
        self.db.commit()

    def create_share_link(self, share_link: PlaylistShare) -> PlaylistShare:
        self.db.add(share_link)
        self.db.commit()
        self.db.refresh(share_link)
        return share_link

    def get_share_by_token(self, token: str) -> PlaylistShare | None:
        return self.db.query(PlaylistShare).filter(PlaylistShare.token == token).first()

    def increment_click_count(self, share_link: PlaylistShare) -> None:
        share_link.click_count += 1
        self.db.commit()

    def update_collaboration_status(self, playlist: Playlist, is_collaborative: bool) -> Playlist:
        playlist.is_collaborative = is_collaborative
        self.db.commit()
        self.db.refresh(playlist)
        return playlist

    def get_collaborator(self, playlist_id: int, user_id: int) -> PlaylistCollaborator | None:
        return self.db.query(PlaylistCollaborator).filter(PlaylistCollaborator.playlist_id == playlist_id, PlaylistCollaborator.user_id == user_id).first()

    def add_collaborator(self, collaborator: PlaylistCollaborator) -> PlaylistCollaborator:
        self.db.add(collaborator)
        self.db.commit()
        self.db.refresh(collaborator)
        return collaborator

    def get_collaborator_by_user_id(self, playlist_id: int, user_id: int) -> PlaylistCollaborator | None:
        return self.db.query(PlaylistCollaborator).filter(PlaylistCollaborator.playlist_id == playlist_id, PlaylistCollaborator.user_id == user_id).first()

    def remove_collaborator(self, collaborator: PlaylistCollaborator) -> None:
        self.db.delete(collaborator)
        self.db.commit()

    def get_public_playlists(self, offset: int, limit: int) -> List[Playlist]:
        return self.db.query(Playlist).filter(Playlist.is_public == True).order_by(Playlist.created_at.desc()).offset(offset).limit(limit).all()

    def count_public_playlists(self) -> int:
        return self.db.query(Playlist).filter(Playlist.is_public == True).count()
