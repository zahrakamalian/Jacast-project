from fastapi import APIRouter, Depends, Form
from typing import Annotated, Optional

from api.dependencies import get_current_user, get_subscription_service
from schemas.subscription import PaginatedResponse, SubscriptionResponse, SubscriptionCreate, SubscriptionUpdate, GroupsListResponse, GroupDetail, GroupCreate
from services.subscription import SubscriptionService
from models.user import User

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
def get_user_subscriptions(user: Annotated[User, Depends(get_current_user)], service: Annotated[SubscriptionService, Depends(get_subscription_service)], limit: int = 10, page: int = 1):
    return service.get_user_subscriptions(user, limit, page)


@router.post("/", response_model=SubscriptionResponse)
def subscribe_channel(user: Annotated[User, Depends(get_current_user)], service: Annotated[SubscriptionService, Depends(get_subscription_service)],
                      data: SubscriptionCreate):
    return service.subscribe_channel(user, data.channel_id)


@router.delete("/{channel_id}")
def unsubscribe_channel(user: Annotated[User, Depends(get_current_user)], service: Annotated[SubscriptionService, Depends(get_subscription_service)],
                        channel_id: int):
    service.unsubscribe_channel(user, channel_id)
    return {"message": "Unsubscribed channel successfully"}


@router.patch("/{id}", response_model=SubscriptionResponse)
def update_subscription(user: Annotated[User, Depends(get_current_user)], service: Annotated[SubscriptionService, Depends(get_subscription_service)],
                        id: int, data: SubscriptionUpdate):
    return service.update_subscription(user, id, data)


@router.get("/groups", response_model=GroupsListResponse)
def get_subscription_groups(user: Annotated[User, Depends(get_current_user)], service: Annotated[SubscriptionService, Depends(get_subscription_service)]):
    return service.get_subscription_groups(user)


@router.post("/groups", response_model=GroupDetail)
def create_subscription_group(data: GroupCreate, user: Annotated[User, Depends(get_current_user)], service: Annotated[SubscriptionService, Depends(get_subscription_service)]):
    return service.create_subscription_group(user, data.name)


@router.put("/groups/{id}", response_model=GroupDetail)
def update_subscription_group(id: int, data: GroupCreate, user: Annotated[User, Depends(get_current_user)], service: Annotated[SubscriptionService, Depends(get_subscription_service)]):
    return service.update_subscription_group(id, user, data.name)


@router.delete("/groups/{id}")
def delete_subscription_group(id: int, user: Annotated[User, Depends(get_current_user)], service: Annotated[SubscriptionService, Depends(get_subscription_service)]):
    service.delete_subscription_group(id, user)
    return {"message": "Subscription group deleted successfully"}


@router.post("/groups/{id}/subscriptions/{subscription_id}", response_model=GroupDetail, status_code=201)
def add_subscription_to_group(id: int, subscription_id: int, user: Annotated[User, Depends(get_current_user)], service: Annotated[SubscriptionService, Depends(get_subscription_service)]):
    return service.add_subscription_to_group(id, subscription_id, user)


@router.delete("/groups/{id}/subscriptions/{subscription_id}")
def remove_subscription_from_group(id: int, subscription_id: int, user: Annotated[User, Depends(get_current_user)], service: Annotated[SubscriptionService, Depends(get_subscription_service)]):
    service.remove_subscription_from_group(id, subscription_id, user)
    return {"message": "Subscription removed from group successfully"}
