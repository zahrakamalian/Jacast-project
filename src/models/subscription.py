from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, String, Float
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
    notifications_enabled = Column(Boolean, default=True)
    custom_name = Column(String, nullable=True)
    playback_speed = Column(Float, default=1.0)
    updated_at = Column(DateTime, default=None, onupdate=func.now())

    subscriber = relationship("User", foreign_keys=[
                              user_id], back_populates="subscriptions")
    channel = relationship("User", foreign_keys=[
                           channel_id], back_populates="channel_subscribers")
    group_items = relationship("GroupItem", back_populates="subscription")


class Group(Base):
    __tablename__ = "subscription_groups"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    group_items = relationship("GroupItem", back_populates="group")


class GroupItem(Base):
    __tablename__ = "subscription_group_items"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey(
        "subscription_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    subscription_id = Column(Integer, ForeignKey(
        "subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(Integer)

    group = relationship("Group", back_populates="group_items")
    subscription = relationship("Subscription", back_populates="group_items")
