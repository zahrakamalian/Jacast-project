from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from connections.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False, index=True)
    channel_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False, index=True)
    subscribed_at = Column(DateTime, default=func.now())

    subscriber = relationship("User", foreign_keys=[
                              user_id], back_populates="subscriptions")
    channel = relationship("User", foreign_keys=[
                           channel_id], back_populates="channel_subscribers")
