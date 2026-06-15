from fastapi import APIRouter, Depends, Query, UploadFile, File
from fastapi.responses import RedirectResponse
from typing import Annotated, List, Optional

from models.user import User
from api.dependencies import get_current_user, get_playlist_service, get_current_user_optional
from services.playlist import PlaylistService
from schemas.playlist import (PlaylistResponse, PlaylistDetailResponse, PlaylistCreate, PlaylistUpdate,
                              PlaylistEpisodesResponse, PlaylistEpisodeResponse, AddEpisodeRequest,
                              ReorderEpisodesRequest, BulkAddResponse, BulkAddRequest, PlaylistShareResponse,
                              CollaborateResponse, CollaborateRequest, AddCollaboratorRequest,
                              CollaboratorResponse, PaginatedPublicPlaylistResponse, PaginatedPlaylistResponse)
router = APIRouter()


@router.get("/", response_model=PaginatedPlaylistResponse)
def get_user_playlists(user: Annotated[User, Depends(get_current_user)], service: Annotated[PlaylistService, Depends(get_playlist_service)],
                       limit: int = Query(10, ge=1, le=100), page: int = Query(1, ge=1)):
    return service.get_user_playlists(user, limit, page)


@router.get("/{id}", response_model=PlaylistDetailResponse)
def get_playlist_detail(id: int, user: Annotated[Optional[User], Depends(get_current_user_optional)],
                        service: Annotated[PlaylistService, Depends(get_playlist_service)]):
    return service.get_playlist_detail(id, user)


@router.post("/", response_model=PlaylistResponse, status_code=201)
def create_playlist(data: PlaylistCreate, user: Annotated[User, Depends(get_current_user)],
                    service: Annotated[PlaylistService, Depends(get_playlist_service)]):
    return service.create_playlist(data, user)


@router.put("/{id}", response_model=PlaylistResponse)
def update_playlist(id: int, data: PlaylistUpdate, user: Annotated[User, Depends(get_current_user)],
                    service: Annotated[PlaylistService, Depends(get_playlist_service)]):
    return service.update_playlist(id, data, user)


@router.delete("/{id}")
def delete_playlist(id: int, user: Annotated[User, Depends(get_current_user)],
                    service: Annotated[PlaylistService, Depends(get_playlist_service)]):
    service.delete_playlist(id, user)
    return {"message": "Playlist deleted successfully"}


@router.patch("/{id}/cover")
async def update_cover_art(user: Annotated[User, Depends(get_current_user)], service: Annotated[PlaylistService, Depends(get_playlist_service)],
                           id: int, image_file: UploadFile = File(...)):
    return await service.update_cover_art(user, id, image_file)


@router.get("/{id}/episodes", response_model=PlaylistEpisodesResponse)
def get_playlist_episodes(id: int, user: Annotated[Optional[User], Depends(get_current_user_optional)],
                          service: Annotated[PlaylistService, Depends(get_playlist_service)]):
    return service.get_playlist_episodes(id, user)


@router.post("/{id}/episodes", response_model=PlaylistEpisodeResponse, status_code=201)
def add_episode_to_playlist(id: int, data: AddEpisodeRequest, user: Annotated[Optional[User], Depends(get_current_user_optional)],
                            service: Annotated[PlaylistService, Depends(get_playlist_service)]):
    return service.add_episode_to_playlist(id, data.podcast_id, user)


@router.delete("/{id}/episodes/{episode_id}")
def remove_episode_from_playlist(id: int, episode_id: int, user: Annotated[User, Depends(get_current_user)],
                                 service: Annotated[PlaylistService, Depends(get_playlist_service)]):
    service.remove_episode_from_playlist(id, episode_id, user)
    return {"message": "Episode removed from playlist successfully"}


@router.patch("/{id}/episodes/reorder")
def reorder_episodes(id: int, data: ReorderEpisodesRequest, user: Annotated[User, Depends(get_current_user)],
                     service: Annotated[PlaylistService, Depends(get_playlist_service)]):
    service.reorder_episodes(id, data, user)
    return {"message": "Episodes reordered successfully"}


@router.post("/{id}/episodes/bulk-add", response_model=BulkAddResponse, status_code=201)
def bulk_add_episodes(id: int, data: BulkAddRequest, user: Annotated[User, Depends(get_current_user)],
                      service: Annotated[PlaylistService, Depends(get_playlist_service)]):
    return service.bulk_add_episodes(id, data, user)


@router.post("/{id}/share", response_model=PlaylistShareResponse)
def create_playlist_share_link(id: int, user: Annotated[User, Depends(get_current_user)],
                               service: Annotated[PlaylistService, Depends(get_playlist_service)]):
    return service.create_playlist_share_link(id, user)


@router.get("/share/{token}")
def redirect_playlist_share(token: str, service: Annotated[PlaylistService, Depends(get_playlist_service)]):
    redirect_url = service.redirect_playlist_share(token)
    return RedirectResponse(url=redirect_url, status_code=302)


@router.post("/{id}/collaborate", response_model=CollaborateResponse)
def update_collaboration_status(id: int, data: CollaborateRequest, user: Annotated[User, Depends(get_current_user)],
                                service: Annotated[PlaylistService, Depends(get_playlist_service)]):
    return service.update_collaboration_status(id, data, user)


@router.post("/{id}/collaborators", response_model=CollaboratorResponse, status_code=201)
def add_collaborator(id: int, data: AddCollaboratorRequest, user: Annotated[User, Depends(get_current_user)],
                     service: Annotated[PlaylistService, Depends(get_playlist_service)]):
    return service.add_collaborator(id, data, user)


@router.delete("/{id}/collaborators/{user_id}")
def remove_collaborator(id: int, user_id: int, user: Annotated[User, Depends(get_current_user)],
                        service: Annotated[PlaylistService, Depends(get_playlist_service)]):
    service.remove_collaborator(id, user_id, user)
    return {"message": "Collaborator removed successfully"}


@router.get("/public/playlists", response_model=PaginatedPublicPlaylistResponse)
def get_public_playlists(service: Annotated[PlaylistService, Depends(get_playlist_service)],
                         limit: int = Query(20, ge=1, le=100), page: int = Query(1, ge=1)):
    return service.get_public_playlists(limit, page)
