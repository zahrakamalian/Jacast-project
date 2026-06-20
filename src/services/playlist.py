import secrets
import uuid
import os

from fastapi import HTTPException, UploadFile
from typing import Optional

from src.config import settings
from src.repository.playlist import PlaylistRepository
from src.repository.podcast import PodcastRepository
from src.repository.user import UserRepository
from src.data.models.playlist import Playlist, PlaylistPodcast, PlaylistShare, PlaylistCollaborator
from src.data.models.user import User
from src.schemas.playlist import (PlaylistResponse, PlaylistDetailResponse, PlaylistOwnerResponse,
                                  PlaylistEpisodeResponse, PlaylistCreate, PlaylistUpdate, PlaylistEpisodesResponse,
                                  PaginatedPlaylistResponse, ReorderEpisodesRequest, BulkAddRequest, BulkAddResponse,
                                  PlaylistShareResponse, CollaborateRequest, CollaborateResponse, AddCollaboratorRequest,
                                  CollaboratorResponse, PaginatedPublicPlaylistResponse, PublicPlaylistResponse)


class PlaylistService:
    def __init__(self, user_repo: UserRepository, playlist_repo: PlaylistRepository, podcast_repo: PodcastRepository):
        self.playlist_repo = playlist_repo
        self.podcast_repo = podcast_repo
        self.user_repo = user_repo

    def _to_playlist_response(self, playlist: Playlist, episodes_count: int) -> PlaylistResponse:
        return PlaylistResponse(
            id=playlist.id,
            title=playlist.title,
            description=playlist.description,
            cover_art_url=playlist.cover_art_url,
            is_public=playlist.is_public,
            episodes_count=episodes_count,
            created_at=playlist.created_at
        )

    def _to_episode_response(self, episode: PlaylistPodcast) -> PlaylistEpisodeResponse:
        return PlaylistEpisodeResponse(
            id=episode.id,
            podcast_id=episode.podcast_id,
            title=episode.podcast.title,
            channel_name=episode.podcast.channel.display_name,
            duration=episode.podcast.duration,
            cover_art_url=episode.podcast.cover_art_url,
            position=episode.position,
            added_at=episode.added_at
        )

    def get_user_playlists(self, user: User, limit: int, page: int) -> PaginatedPlaylistResponse:
        offset = (page - 1) * limit
        playlists = self.playlist_repo.get_user_playlists(
            user.id, offset, limit)
        total = self.playlist_repo.count_user_playlists(user.id)

        items = []
        for playlist in playlists:
            episodes_count = len(playlist.episodes) if playlist.episodes else 0
            item = self._to_playlist_response(playlist, episodes_count)
            items.append(item)

        pages = (total + limit - 1) // limit
        has_next = page < pages
        has_prev = page > 1

        return PaginatedPlaylistResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )

    def get_playlist_detail(self, id: int, user: Optional[User]) -> PlaylistDetailResponse:
        playlist = self.playlist_repo.get_playlist_by_id(id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        if not playlist.is_public and (not user or playlist.user_id != user.id):
            raise HTTPException(status_code=403, detail="Unauthorized")

        owner = PlaylistOwnerResponse(
            id=playlist.user_id,
            display_name=playlist.user.display_name,
            avatar_url=playlist.user.avatar_url
        )

        episodes = []
        for episode in playlist.episodes:
            item = self._to_episode_response(episode)
            episodes.append(item)

        episodes.sort(key=lambda x: x.position)

        return PlaylistDetailResponse(
            id=playlist.id,
            title=playlist.title,
            description=playlist.description,
            cover_art_url=playlist.cover_art_url,
            is_public=playlist.is_public,
            created_at=playlist.created_at,
            owner=owner,
            episodes=episodes
        )

    def create_playlist(self, data: PlaylistCreate, user: User) -> PlaylistResponse:
        playlist = self.playlist_repo.get_playlist_by_user_and_title(
            user.id, data.title)
        if playlist:
            raise HTTPException(
                status_code=400, detail="Playlist already exists")

        new_entry = Playlist(
            user_id=user.id,
            title=data.title,
            description=data.description,
            cover_art_url=data.cover_art_url,
            is_public=data.is_public
        )

        new_playlist = self.playlist_repo.create_playlist(new_entry)
        return self._to_playlist_response(new_playlist, 0)

    def update_playlist(self, id: int,  data: PlaylistUpdate, user: User) -> PlaylistResponse:
        playlist = self.playlist_repo.get_playlist_by_id(id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        if playlist.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="You are not allowed to modify this playlist")

        if data.title and data.title != playlist.title:
            existing = self.playlist_repo.get_playlist_by_user_and_title(
                user.id, data.title)
            if existing:
                raise HTTPException(
                    status_code=400, detail="A playlist with this title already exists")

        updated_playlist = self.playlist_repo.update_playlist(
            playlist, data.title, data.description, data.is_public, data.cover_art_url)
        episodes_count = self.playlist_repo.count_playlist_episodes(
            updated_playlist.id)

        return self._to_playlist_response(updated_playlist, episodes_count)

    def delete_playlist(self, id: int, user: User) -> None:
        playlist = self.playlist_repo.get_playlist_by_id(id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        if playlist.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="You are not allowed to delete this playlist")

        self.playlist_repo.delete_playlist(playlist)

    async def update_cover_art(self,  user: User, id: int, image_file: UploadFile) -> PlaylistResponse:
        if not image_file or image_file.size == 0:
            raise HTTPException(
                status_code=400, detail="Cover image is required")

        playlist = self.playlist_repo.get_playlist_by_id(id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        if playlist.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="You are not allowed to update cover image")

        if playlist.cover_art_url:
            self.playlist_repo.delete_playlist_cover_file(
                playlist.cover_art_url)

        MAX_IMAGE_SIZE = 5 * 1024 * 1024
        IMAGE_SUFFIXES = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp"
        }
        if image_file.content_type not in IMAGE_SUFFIXES:
            raise HTTPException(
                status_code=415, detail="Unsupported image format")

        image_extension = IMAGE_SUFFIXES[image_file.content_type]
        image_unique_name = f"cover_{user.id}_{uuid.uuid4().hex}{image_extension}"

        image_file_path = settings.PLAYLIST_COVER_DIR / image_unique_name

        content = await image_file.read()
        if len(content) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400, detail="Image too large. Max 5MB")
        with open(image_file_path, "wb") as f:
            f.write(content)
        if os.getenv("RENDER"):
            cover_url = f"/temp-covers/{image_unique_name}"
        else:
            cover_url = f"/resources/uploads/images/{image_unique_name}"

        updated_playlist = self.playlist_repo.update_cover_art_url(
            playlist, cover_url)
        episodes_count = self.playlist_repo.count_playlist_episodes(
            updated_playlist.id)
        return self._to_playlist_response(updated_playlist, episodes_count)

    def get_playlist_episodes(self, playlist_id: int, user: Optional[User] = None) -> PlaylistEpisodesResponse:
        playlist = self.playlist_repo.get_playlist_by_id(playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        if not playlist.is_public and (not user or playlist.user_id != user.id):
            raise HTTPException(status_code=403, detail="Unauthorized")

        episodes = []
        for episode in playlist.episodes:
            item = self._to_episode_response(episode)
            episodes.append(item)

        episodes.sort(key=lambda x: x.position)

        return PlaylistEpisodesResponse(
            playlist_id=playlist.id,
            playlist_title=playlist.title,
            total=len(episodes),
            episodes=episodes
        )

    def add_episode_to_playlist(self, id: int, podcast_id: int, user: User) -> PlaylistEpisodeResponse:
        playlist = self.playlist_repo.get_playlist_by_id(id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        if playlist.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="You are not allowed to modify this playlist")

        podcast = self.podcast_repo.get_podcast_by_id(podcast_id)
        if not podcast:
            raise HTTPException(status_code=404, detail="Podcast not found")

        existing = self.playlist_repo.get_playlist_episode(id, podcast_id)
        if existing:
            raise HTTPException(
                status_code=400, detail="Episode already in this playlist")

        new_position = self.playlist_repo.get_last_position_in_playlist(id)

        new_episode = PlaylistPodcast(
            playlist_id=id,
            podcast_id=podcast_id,
            position=new_position
        )

        created_episode = self.playlist_repo.add_episode_to_playlist(
            new_episode)
        return self._to_episode_response(created_episode)

    def remove_episode_from_playlist(self, playlist_id: int, episode_id: int, user: User) -> None:
        playlist = self.playlist_repo.get_playlist_by_id(playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        if playlist.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="You are not allowed to modify this playlist")

        episode = self.playlist_repo.get_playlist_episode_by_id(episode_id)
        if not episode:
            raise HTTPException(
                status_code=404, detail="Episode not found in this playlist")

        if episode.playlist_id != playlist_id:
            raise HTTPException(
                status_code=400, detail="Episode does not belong to this playlist")

        deleted_position = episode.position
        self.playlist_repo.delete_playlist_episode(episode)
        self.playlist_repo.reorder_positions_after_deletion(
            playlist_id, deleted_position)

    def reorder_episodes(self, id: int, data: ReorderEpisodesRequest, user: User) -> None:
        playlist = self.playlist_repo.get_playlist_by_id(id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        if playlist.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="You are not allowed to modify this playlist")

        episodes = self.playlist_repo.get_all_episodes_by_playlist_id(id)
        if len(episodes) != len(data.order):
            raise HTTPException(
                status_code=400, detail="Reorder all the episodes")

        episode_ids = {episode.id for episode in episodes}
        for episode_id in data.order:
            if episode_id not in episode_ids:
                raise HTTPException(
                    status_code=400, detail=f"Invalid episode id: {episode_id}")

        updates = []
        for index, episode_id in enumerate(data.order):
            updates.append((episode_id, index))

        self.playlist_repo.bulk_update_episode_positions(updates)

    def bulk_add_episodes(self, id: int, data: BulkAddRequest, user: User) -> BulkAddResponse:
        playlist = self.playlist_repo.get_playlist_by_id(id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        if playlist.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="You are not allowed to modify this playlist")

        existing_podcast_ids = self.playlist_repo.get_existing_episode_ids(id)
        position = self.playlist_repo.get_last_position_in_playlist(id)

        skipped_ids = []
        new_episodes = []
        counter = 0
        for podcast_id in data.podcast_ids:
            if podcast_id in existing_podcast_ids:
                skipped_ids.append(podcast_id)
            else:
                item = PlaylistPodcast(
                    podcast_id=podcast_id,
                    playlist_id=id,
                    position=position + counter
                )
                new_episodes.append(item)
                counter += 1

        if len(new_episodes) > 0:
            self.playlist_repo.bulk_add_episodes(new_episodes)

        return BulkAddResponse(
            message=f"{len(new_episodes)} episodes added, {len(skipped_ids)} skipped",
            added_count=len(new_episodes),
            skipped_count=len(skipped_ids),
            skipped_ids=skipped_ids
        )

    def create_playlist_share_link(self, id: int, user: User) -> PlaylistShareResponse:
        playlist = self.playlist_repo.get_playlist_by_id(id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        if playlist.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="You are not allowed to share this playlist")

        token = secrets.token_urlsafe(12)
        new_share = PlaylistShare(
            playlist_id=id,
            token=token
        )
        self.playlist_repo.create_share_link(new_share)
        share_url = f"https://jacast.com/share/playlist/{token}"

        return PlaylistShareResponse(
            share_url=share_url,
            token=token
        )

    def redirect_playlist_share(self, token: str) -> str:
        share_link = self.playlist_repo.get_share_by_token(token)
        if not share_link:
            raise HTTPException(
                status_code=404, detail="Invalid or expired share link")
        self.playlist_repo.increment_click_count(share_link)
        return f"/playlists/{share_link.playlist_id}"

    def update_collaboration_status(self, playlist_id: int, data: CollaborateRequest, user: User) -> CollaborateResponse:
        playlist = self.playlist_repo.get_playlist_by_id(playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        if playlist.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="Only the owner can change collaboration settings")

        updated_playlist = self.playlist_repo.update_collaboration_status(
            playlist, data.is_collaborative)
        status_text = "enabled" if data.is_collaborative else "disabled"

        return CollaborateResponse(
            message=f"Collaboration {status_text} successfully",
            is_collaborative=updated_playlist.is_collaborative
        )

    def add_collaborator(self, playlist_id: int, data: AddCollaboratorRequest, current_user: User) -> CollaboratorResponse:
        playlist = self.playlist_repo.get_playlist_by_id(playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        if playlist.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Only the owner can add collaborators")

        if not playlist.is_collaborative:
            raise HTTPException(
                status_code=400, detail="Collaboration is not enabled for this playlist")

        user = self.user_repo.get_user_by_id(data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.id == current_user.id:
            raise HTTPException(
                status_code=400, detail="You cannot add yourself as a collaborator")

        existing = self.playlist_repo.get_collaborator(playlist_id, user.id)
        if existing:
            raise HTTPException(
                status_code=400, detail="User is already a collaborator")

        new_entry = PlaylistCollaborator(
            playlist_id=playlist_id,
            user_id=user.id,
            permission=data.permission
        )

        new_collaborator = self.playlist_repo.add_collaborator(new_entry)
        return CollaboratorResponse(
            id=new_collaborator.id,
            playlist_id=new_collaborator.playlist_id,
            user_id=new_collaborator.user_id,
            user_name=user.display_name,
            user_avatar=user.avatar_url,
            permission=new_collaborator.permission,
            added_at=new_collaborator.added_at
        )

    def remove_collaborator(self, playlist_id: int, user_id: int, user: User) -> None:
        playlist = self.playlist_repo.get_playlist_by_id(playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        if playlist.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="Only the owner can remove collaborators")

        collaborator = self.playlist_repo.get_collaborator_by_user_id(
            playlist_id, user_id)
        if not collaborator:
            raise HTTPException(
                status_code=404, detail="Collaborator not found")
        self.playlist_repo.remove_collaborator(collaborator)

    def get_public_playlists(self, limit: int = 20, page: int = 1) -> PaginatedPublicPlaylistResponse:
        offset = (page - 1) * limit
        playlists = self.playlist_repo.get_public_playlists(offset, limit)
        total = self.playlist_repo.count_public_playlists()

        items = []
        for playlist in playlists:
            episodes_count = len(playlist.episodes) if playlist.episodes else 0
            item = PublicPlaylistResponse(
                id=playlist.id,
                title=playlist.title,
                description=playlist.description,
                cover_art_url=playlist.cover_art_url,
                owner_name=playlist.user.display_name,
                owner_avatar=playlist.user.avatar_url,
                episodes_count=episodes_count,
                created_at=playlist.created_at
            )
            items.append(item)

        pages = (total + limit - 1) // limit
        has_next = page < pages
        has_prev = page > 1

        return PaginatedPublicPlaylistResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )
