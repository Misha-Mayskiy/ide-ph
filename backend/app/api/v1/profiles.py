from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.core.security import AuthUser, get_current_user
from app.models.profile import IdeProfile
from app.schemas.ide_config import normalize_ide_config
from app.schemas.profile import (
    ProfileCreateRequest,
    ProfileListResponse,
    ProfileResponse,
    ProfileUpdateRequest,
)

router = APIRouter(prefix="/profiles")


def _to_schema(profile: IdeProfile) -> ProfileResponse:
    return ProfileResponse(
        id=profile.id,
        name=profile.name,
        ideConfig=normalize_ide_config(profile.ide_config),
        createdAt=profile.created_at,
        updatedAt=profile.updated_at,
    )


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    payload: ProfileCreateRequest,
    user: AuthUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ProfileResponse:
    profile = IdeProfile(
        user_id=user.user_id,
        name=payload.name,
        ide_config=normalize_ide_config(payload.ideConfig).model_dump(mode="json"),
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return _to_schema(profile)


@router.get("", response_model=ProfileListResponse)
async def list_profiles(
    user: AuthUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ProfileListResponse:
    stmt = select(IdeProfile).where(IdeProfile.user_id == user.user_id).order_by(IdeProfile.updated_at.desc())
    profiles = (await session.execute(stmt)).scalars().all()
    return ProfileListResponse(items=[_to_schema(p) for p in profiles])


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: str,
    user: AuthUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ProfileResponse:
    stmt = select(IdeProfile).where(IdeProfile.id == profile_id, IdeProfile.user_id == user.user_id)
    profile = (await session.execute(stmt)).scalar_one_or_none()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Profile not found"},
        )
    return _to_schema(profile)


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: str,
    payload: ProfileUpdateRequest,
    user: AuthUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ProfileResponse:
    stmt = select(IdeProfile).where(IdeProfile.id == profile_id, IdeProfile.user_id == user.user_id)
    profile = (await session.execute(stmt)).scalar_one_or_none()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Profile not found"},
        )

    if payload.name is not None:
        profile.name = payload.name
    if payload.ideConfig is not None:
        profile.ide_config = normalize_ide_config(payload.ideConfig).model_dump(mode="json")

    await session.commit()
    await session.refresh(profile)
    return _to_schema(profile)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: str,
    user: AuthUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    stmt = select(IdeProfile).where(IdeProfile.id == profile_id, IdeProfile.user_id == user.user_id)
    profile = (await session.execute(stmt)).scalar_one_or_none()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Profile not found"},
        )

    await session.delete(profile)
    await session.commit()
