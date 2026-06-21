from src.data.models.subscription import Subscription, Group, GroupItem


def create_subscription(user_id, channel_id):
    return Subscription(
        user_id=user_id,
        channel_id=channel_id,
    )


def create_group(user_id, name="Favorites"):
    return Group(
        user_id=user_id,
        name=name,
    )


def create_group_item(group_id, subscription_id, position=0):
    return GroupItem(
        group_id=group_id,
        subscription_id=subscription_id,
        position=position,
    )
