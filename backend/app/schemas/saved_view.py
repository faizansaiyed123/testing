from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

ViewEntity = Literal["company", "contact", "opportunity", "task"]


class SavedViewCreate(BaseModel):
    entity_type: ViewEntity
    name: str = Field(min_length=1, max_length=120)
    filters: dict[str, Any] = Field(default_factory=dict)
    columns: list[str] = Field(default_factory=list, max_length=30)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("View name cannot be blank")
        return value

    @field_validator("filters")
    @classmethod
    def validate_filters(cls, value: dict[str, Any]) -> dict[str, Any]:
        if len(value) > 32:
            raise ValueError("A saved view can contain at most 32 filters")
        return value

    @field_validator("columns")
    @classmethod
    def validate_columns(cls, value: list[str]) -> list[str]:
        if any(not column or len(column) > 64 for column in value):
            raise ValueError("Saved view columns must be non-empty and <= 64 characters")
        if len(set(value)) != len(value):
            raise ValueError("Saved view columns must be unique")
        return value


class SavedViewUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    filters: dict[str, Any] | None = None
    columns: list[str] | None = Field(default=None, max_length=30)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = " ".join(value.split())
        if not value:
            raise ValueError("View name cannot be blank")
        return value

    @field_validator("filters")
    @classmethod
    def validate_filters(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is not None and len(value) > 32:
            raise ValueError("A saved view can contain at most 32 filters")
        return value

    @field_validator("columns")
    @classmethod
    def validate_columns(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        if any(not column or len(column) > 64 for column in value):
            raise ValueError("Saved view columns must be non-empty and <= 64 characters")
        if len(set(value)) != len(value):
            raise ValueError("Saved view columns must be unique")
        return value


class SavedViewResponse(BaseModel):
    id: UUID
    organization_id: UUID
    owner_user_id: UUID
    entity_type: ViewEntity
    name: str
    filters: dict[str, Any]
    columns: list[str]
    created_at: datetime
    updated_at: datetime


class SavedViewListResponse(BaseModel):
    items: list[SavedViewResponse]
