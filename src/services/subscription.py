from fastapi import HTTPException
from typing import Optional

from repository.subscription import SubscriptionRepository
from repository.user import UserRepository
from models.user import User
from models.subscription import Subscription, Group, GroupItem
from schemas.subscription import PaginatedResponse, SubscriptionResponse, SubscriptionUpdate, SubscriptionDetail, GroupsListResponse, GroupDetail


class SubscriptionService:
    def __init__(self, sub_repo: SubscriptionRepository, user_repo: UserRepository):
        self.sub_repo = sub_repo
        self.user_repo = user_repo

    def _to_response(self, subscription: Subscription) -> SubscriptionResponse:
        return SubscriptionResponse(
            id=subscription.channel_id,
            title=subscription.channel.title,
            channel_name=subscription.channel.display_name,
            cover_art_url=subscription.channel.cover_art_url,
            duration=subscription.channel.duration,
            created_at=subscription.channel.created_at,
            subscribed_at=subscription.subscribed_at,
            notifications_enabled=subscription.notifications_enabled,
            custom_name=subscription.custom_name,
            playback_speed=subscription.playback_speed
        )

    def _to_subscription_detail(self, group_item: GroupItem) -> SubscriptionDetail:
        return SubscriptionDetail(
            id=group_item.subscription.channel_id,
            title=group_item.subscription.channel.title,
            channel_name=group_item.subscription.channel.display_name,
            cover_art_url=group_item.subscription.channel.cover_art_url,
            duration=group_item.subscription.channel.duration,
            created_at=group_item.subscription.channel.created_at,
            subscribed_at=group_item.subscription.subscribed_at
        )

    def _to_group_detail(self, group: Group) -> GroupDetail:
        subscription_details = [
            self._to_subscription_detail(group_item)
            for group_item in group.group_items
        ]
        return GroupDetail(
            id=group.id,
            name=group.name,
            subscriptions=subscription_details
        )

    def _group_validation(self, user: User, group_id: int):
        group = self.sub_repo.get_group_by_id(group_id)
        if not group:
            raise HTTPException(
                status_code=404, detail="Subscription group not found")

        if group.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="You are not allowed to modify this group")
        return group

    def get_user_subscriptions(self, user: User, limit: int, page: int) -> PaginatedResponse:
        offset = (page - 1) * limit

        subscriptions = self.sub_repo.get_user_subscriptions(
            user.id, limit, offset)
        items = []
        for subscription in subscriptions:
            item = self._to_response(subscription)
            items.append(item)

        total = self.sub_repo.get_user_subscriptions_count(user.id)
        pages = (total + limit - 1) // limit
        has_next = page < pages
        has_prev = page > 1

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )

    def subscribe_channel(self, user: User, channel_id: int) -> SubscriptionResponse:
        channel = self.user_repo.get_user_by_id(channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")

        if not channel.is_channel:
            raise HTTPException(
                status_code=400, detail="You can only subscribe to channels")

        if user.id == channel_id:
            raise HTTPException(
                status_code=400, detail="You cannot subscribe to your own channel")

        subscription = self.sub_repo.get_subscription_by_user_and_channel(
            user.id, channel_id)
        if subscription:
            raise HTTPException(
                status_code=400, detail="You have already Subscribed this channel")

        new_entry = Subscription(
            user_id=user.id,
            channel_id=channel_id
        )

        new_subscription = self.sub_repo.subscribe_channel(new_entry)

        return self._to_response(new_subscription)

    def unsubscribe_channel(self, user: User, channel_id: int) -> None:
        channel = self.user_repo.get_user_by_id(channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")

        if user.id == channel_id:
            raise HTTPException(
                status_code=400, detail="You cannot Unsubscribe your own channel")

        subscription = self.sub_repo.get_subscription_by_user_and_channel(
            user.id, channel_id)
        if not subscription:
            raise HTTPException(
                status_code=400, detail="You haven't Subscribed this channel")

        self.sub_repo.unsubscribe_channel(subscription)

    def update_subscription(self, user: User, sub_id: int, data: SubscriptionUpdate) -> SubscriptionResponse:
        subscription = self.sub_repo.get_subscription_by_id(sub_id)
        if not subscription:
            raise HTTPException(
                status_code=404, detail="Subscription not found")
        if subscription.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="You are not the owner of this subscription")

        updated_subscription = self.sub_repo.update_subscription(
            subscription, data.notifications_enabled, data.custom_name, data.playback_speed)

        return self._to_response(updated_subscription)

    def get_subscription_groups(self, user: User) -> GroupsListResponse:
        groups = self.sub_repo.get_subscription_groups(user.id)
        groups_list = []
        for group in groups:
            group_detail = self._to_group_detail(group)
            groups_list.append(group_detail)

        return GroupsListResponse(groups=groups_list)

    def create_subscription_group(self, user: User, name: str) -> GroupDetail:
        group = self.sub_repo.get_subscription_group_by_name_and_user(
            user.id, name)
        if group:
            raise HTTPException(
                status_code=400, detail="Group with this name already exists")

        new_entry = Group(
            user_id=user.id,
            name=name
        )
        new_group = self.sub_repo.create_subscription_group(new_entry)

        return self._to_group_detail(new_group)

    def update_subscription_group(self, id: int, user: User, name: str) -> GroupDetail:
        group = self._group_validation(user, id)
        if group.name == name:
            raise HTTPException(
                status_code=400, detail="Please choose a different name")

        existing_group = self.sub_repo.get_subscription_group_by_name_and_user(
            user.id, name)
        if existing_group and existing_group.id != group.id:
            raise HTTPException(400, "A group with this name already exists")

        updated_group = self.sub_repo.update_subscription_group(group, name)
        subscription_details = []
        for group_item in updated_group.group_items:
            sub_detail = self._to_subscription_detail(group_item)
            subscription_details.append(sub_detail)

        return GroupDetail(
            id=updated_group.id,
            name=updated_group.name,
            subscriptions=subscription_details
        )

    def delete_subscription_group(self, id: int, user: User):
        group = self.sub_repo.get_group_by_id(id)
        if not group:
            raise HTTPException(
                status_code=404, detail="Subscription group not found")

        if group.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="You are not allowed to delete this group")

        self.sub_repo.delete_subscription_group(group)

    def add_subscription_to_group(self, id: int, subscription_id: int, user: User) -> GroupDetail:
        group = self._group_validation(user, id)
        subscription = self.sub_repo.get_subscription_by_id(subscription_id)
        if not subscription:
            raise HTTPException(
                status_code=404, detail="Subscription not found")

        existing = self.sub_repo.get_group_item_by_group_and_subscription(
            group.id, subscription.id)
        if existing:
            raise HTTPException(
                status_code=400, detail="Subscription already in this group")

        new_entry = GroupItem(
            group_id=group.id,
            subscription_id=subscription.id,
            position=self.sub_repo.get_last_position_in_group(group.id)
        )
        new_item = self.sub_repo.add_subscription_to_group(new_entry)
        updated_group = self.sub_repo.get_group_by_id(new_item.group_id)
        return self._to_group_detail(updated_group)

    def remove_subscription_from_group(self, id: int, subscription_id: int, user: User) -> None:
        group = self._group_validation(user, id)
        subscription = self.sub_repo.get_subscription_by_id(subscription_id)
        if not subscription:
            raise HTTPException(
                status_code=404, detail="Subscription not found")

        if subscription.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="You are not the owner of this subscription")

        group_item = self.sub_repo.get_group_item_by_group_and_subscription(
            group.id, subscription.id)
        if not group_item:
            raise HTTPException(
                status_code=400, detail="Subscription does not exist in this group")

        self.sub_repo.remove_subscription_from_group(group_item)
