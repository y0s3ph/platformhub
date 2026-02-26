"""Pydantic schemas for API request/response validation."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from platformhub.models import RequestStatus, ResourceType, Role


# --- Auth ---


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: Role
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Resource catalog ---


class CatalogItem(BaseModel):
    resource_type: ResourceType
    display_name: str
    description: str
    parameters: list[ParameterSpec]


class ParameterSpec(BaseModel):
    name: str
    label: str
    type: str = "string"
    required: bool = True
    default: str | None = None
    options: list[str] | None = None
    description: str = ""


CatalogItem.model_rebuild()


# --- Resource requests ---


class ResourceRequestCreate(BaseModel):
    resource_type: ResourceType
    name: str = Field(min_length=3, max_length=100, pattern=r"^[a-z][a-z0-9-]*$")
    environment: str = Field(pattern=r"^(dev|staging|production)$")
    parameters: dict[str, str] = Field(default_factory=dict)


class ResourceRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resource_type: ResourceType
    name: str
    environment: str
    parameters: str
    status: RequestStatus
    generated_manifest: str | None
    requester_id: int
    reviewer_id: int | None
    review_comment: str | None
    created_at: datetime
    reviewed_at: datetime | None


class ReviewAction(BaseModel):
    action: RequestStatus = Field(description="Must be 'approved' or 'rejected'")
    comment: str = ""
