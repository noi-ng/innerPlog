import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.core.const import PostStatus
from src.schemas.category import CategoryResponse


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    content: str = Field(min_length=1)
    status: PostStatus = PostStatus.DRAFT
    tags: list[str] = []
    category_ids: list[UUID] = []

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be blank")
        return v.strip()

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        cleaned = []
        for tag in v:
            tag = tag.strip().lower()
            if not tag:
                continue
            if not re.fullmatch(r"[a-zA-Z0-9_\- ]+", tag):
                raise ValueError(
                    f"Tag '{tag}' contains invalid characters. "
                    "Only letters, digits, spaces, hyphens and underscores allowed"
                )
            if len(tag) > 50:
                raise ValueError(f"Tag '{tag}' exceeds 50 characters")
            cleaned.append(tag)
        return cleaned

    @field_validator("status")
    @classmethod
    def user_cannot_set_banned(cls, v: PostStatus) -> PostStatus:
        if v == PostStatus.BANNED:
            raise ValueError("Users cannot set post status to 'banned'")
        return v


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=300)
    content: str | None = None
    status: PostStatus | None = None
    tags: list[str] | None = None
    category_ids: list[UUID] | None = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Title cannot be blank")
        return v.strip() if v else v

    @field_validator("content")
    @classmethod
    def content_not_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("Content cannot be blank")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        cleaned = []
        for tag in v:
            tag = tag.strip().lower()
            if not tag:
                continue
            if not re.fullmatch(r"[a-zA-Z0-9_\- ]+", tag):
                raise ValueError(
                    f"Tag '{tag}' contains invalid characters. "
                    "Only letters, digits, spaces, hyphens and underscores allowed"
                )
            if len(tag) > 50:
                raise ValueError(f"Tag '{tag}' exceeds 50 characters")
            cleaned.append(tag)
        return cleaned

    @field_validator("status")
    @classmethod
    def user_cannot_set_banned(cls, v: PostStatus | None) -> PostStatus | None:
        if v is not None and v == PostStatus.BANNED:
            raise ValueError("Users cannot set post status to 'banned'")
        return v


class PostAuthorResponse(BaseModel):
    id: UUID
    username: str
    fullname: str | None = None

    model_config = {"from_attributes": True}


class PostResponse(BaseModel):
    id: UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    status: str
    tags: list[str]
    author_id: UUID
    author: PostAuthorResponse
    categories: list[CategoryResponse] = []

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    items: list[PostResponse]
    total: int
    page: int
    page_size: int


class AdminPostUpdate(BaseModel):
    status: PostStatus
