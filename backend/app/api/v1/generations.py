from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.core.security import AuthUser, get_current_user
from app.models.generation import GenerationJob
from app.schemas.generation import (
    GenerationCreateRequest,
    GenerationCreateResponse,
    GenerationStatusResponse,
)

router = APIRouter(prefix="/generations")


@router.post("", response_model=GenerationCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_generation(
    payload: GenerationCreateRequest,
    request: Request,
    user: AuthUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> GenerationCreateResponse:
    # Keep only latest generation record per user for MVP history policy.
    await session.execute(delete(GenerationJob).where(GenerationJob.user_id == user.user_id))

    job = GenerationJob(
        user_id=user.user_id,
        prompt=payload.prompt,
        locale=payload.locale,
        status="queued",
        progress=0,
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    return GenerationCreateResponse(
        generationId=job.id,
        status=job.status,
        pollUrl=str(request.url_for("get_generation_status", generation_id=job.id)),
    )


@router.get("/{generation_id}", response_model=GenerationStatusResponse, name="get_generation_status")
async def get_generation_status(
    generation_id: str,
    user: AuthUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> GenerationStatusResponse:
    stmt = select(GenerationJob).where(
        GenerationJob.id == generation_id,
        GenerationJob.user_id == user.user_id,
    )
    job = (await session.execute(stmt)).scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Generation job not found"},
        )

    return GenerationStatusResponse(
        status=job.status,
        progress=job.progress,
        ideConfig=job.ide_config,
        error=job.error,
    )
