from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional, List


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    podcasts_count: int = Field(ge=0)
    created_at: datetime


class PaginatedCategoryResponse(BaseModel):
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=50)
    pages: int = Field(..., ge=0)
    items: List[CategoryResponse] = Field(default=[])
