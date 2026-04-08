from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ide_config import IdeConfig


GenerationStatus = Literal["queued", "running", "succeeded", "failed"]
Locale = Literal["ru", "en"]


class GenerationCreateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    prompt: str = Field(min_length=3, max_length=3000)
    locale: Locale = "ru"


class GenerationCreateResponse(BaseModel):
    generationId: str
    status: GenerationStatus
    pollUrl: str


class GenerationStatusResponse(BaseModel):
    status: GenerationStatus
    progress: int = Field(default=0, ge=0, le=100)
    ideConfig: IdeConfig | None = None
    error: dict | None = None
