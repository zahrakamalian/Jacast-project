from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


from src.data.database.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())

    podcasts = relationship("CategoryPodcast", back_populates="category")


class CategoryPodcast(Base):
    __tablename__ = "podcast_categories"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey(
        "categories.id", ondelete="CASCADE"), nullable=False, index=True)
    podcast_id = Column(Integer, ForeignKey(
        "podcasts.id", ondelete="CASCADE"), nullable=False, index=True)
    position = Column(Integer)

    podcast = relationship("Podcast", back_populates="categories")
    category = relationship("Category", back_populates="podcasts")
