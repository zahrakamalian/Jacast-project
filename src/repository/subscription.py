from datetime import datetime, timezone

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from src.data.models.subscription import Subscription, Group, GroupItem
from src.data.models.user import User


class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_total_subscribers(self, channel_id: int) -> int:
        return self.db.query(Subscription).filter(Subscription.channel_id == channel_id).count()

    def get_podcast_subscribers(self, channel_id: int) -> list[User]:
        return self.db.query(User).join(Subscription, Subscription.user_id == User.id)\
            .filter(Subscription.channel_id == channel_id).all()

    def get_user_subscriptions(self, user_id: int, limit: int, offset: int):
        return self.db.query(Subscription).options(joinedload(Subscription.channel))\
            .filter(Subscription.user_id == user_id).order_by(Subscription.subscribed_at.desc()).limit(limit).offset(offset).all()

    def get_user_subscriptions_count(self, user_id: int) -> int:
        return self.db.query(Subscription).filter(Subscription.user_id == user_id).count()

    def get_subscription_by_user_and_channel(self, user_id, channel_id) -> Subscription | None:
        return self.db.query(Subscription).options(joinedload(Subscription.channel))\
            .filter(Subscription.user_id == user_id, Subscription.channel_id == channel_id).first()

    def subscribe_channel(self, sub: Subscription) -> Subscription:
        self.db.add(sub)
        self.db.commit()
        self.db.refresh(sub)
        return sub

    def unsubscribe_channel(self, sub: Subscription) -> None:
        self.db.delete(sub)
        self.db.commit()

    def get_subscription_by_id(self, id: int) -> Subscription | None:
        return self.db.query(Subscription).options(joinedload(Subscription.channel)).filter(Subscription.id == id).first()

    def update_subscription(self, subscription: Subscription, notifications_enabled: Optional[bool] = None,
                            custom_name: Optional[str] = None, playback_speed: Optional[float] = None) -> Subscription | None:
        if notifications_enabled is not None and notifications_enabled != subscription.notifications_enabled:
            subscription.notifications_enabled = notifications_enabled
        if custom_name is not None and custom_name != subscription.custom_name:
            subscription.custom_name = custom_name
        if playback_speed is not None and playback_speed != subscription.playback_speed:
            subscription.playback_speed = playback_speed

        subscription.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription

    def get_subscription_groups(self, user_id: int) -> List[Group]:
        return self.db.query(Group).options(joinedload(Group.group_items).joinedload(GroupItem.subscription).joinedload(Subscription.channel))\
            .filter(Group.user_id == user_id).order_by(Group.created_at.asc()).all()

    def get_subscription_group_by_name_and_user(self, user_id: int, group_name: str) -> Group | None:
        return self.db.query(Group).filter(Group.user_id == user_id, Group.name == group_name).first()

    def create_subscription_group(self, group: Group) -> Group:
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group

    def get_group_by_id(self, id: int) -> Group | None:
        return self.db.query(Group).options(joinedload(Group.group_items).joinedload(GroupItem.subscription).joinedload(Subscription.channel))\
            .filter(Group.id == id).first()

    def update_subscription_group(self, group: Group, name: str) -> Group:
        group.name = name
        self.db.commit()
        self.db.refresh(group)
        return group

    def delete_subscription_group(self, group: Group) -> None:
        self.db.delete(group)
        self.db.commit()

    def get_group_item_by_group_and_subscription(self, group_id: int, subscription_id: int) -> GroupItem | None:
        return self.db.query(GroupItem).filter(GroupItem.group_id == group_id, GroupItem.subscription_id == subscription_id).first()

    def get_last_position_in_group(self, group_id: int) -> int:
        result = self.db.query(func.max(GroupItem.position)).filter(
            GroupItem.group_id == group_id).scalar()
        return (result + 1) if result is not None else 0

    def add_subscription_to_group(self, item: GroupItem) -> GroupItem:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def remove_subscription_from_group(self, item: GroupItem) -> None:
        self.db.delete(item)
        self.db.commit()
