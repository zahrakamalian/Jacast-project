from models.subscription import Subscription
from models.user import User
from sqlalchemy.orm import Session


class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_total_subscribers(self, channel_id: int) -> int:
        return self.db.query(Subscription).filter(Subscription.channel_id == channel_id).count()

    def get_podcast_subscribers(self, channel_id: int) -> list[User] | None:
        return self.db.query(User).join(Subscription, Subscription.user_id == User.id).filter(Subscription.channel_id == channel_id).all()
