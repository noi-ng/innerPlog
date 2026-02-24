import re
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def name_valid(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Category name cannot be blank")
        if not re.fullmatch(r"[a-zA-Z0-9 _\-&]+", v):
            raise ValueError(
                "Category name can only contain letters, digits, "
                "spaces, hyphens, underscores, and ampersands"
            )
        return v


class CategoryUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def name_valid(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Category name cannot be blank")
        if not re.fullmatch(r"[a-zA-Z0-9 _\-&]+", v):
            raise ValueError(
                "Category name can only contain letters, digits, "
                "spaces, hyphens, underscores, and ampersands"
            )
        return v


class CategoryResponse(BaseModel):
    id: UUID
    name: str

    model_config = {"from_attributes": True}
