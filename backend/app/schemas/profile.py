from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ide_config import IdeConfig


class ProfileCreateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = Field(min_length=1, max_length=120)
    ideConfig: IdeConfig


class ProfileUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str | None = Field(default=None, min_length=1, max_length=120)
    ideConfig: IdeConfig | None = None


class ProfileResponse(BaseModel):
    id: str
    name: str
    ideConfig: IdeConfig
    createdAt: datetime
    updatedAt: datetime


class ProfileListResponse(BaseModel):
    items: list[ProfileResponse]
