from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.generation import GenerationHistory, GenerationJob


async def upsert_history(session: AsyncSession, job: GenerationJob) -> None:
    stmt = select(GenerationHistory).where(GenerationHistory.user_id == job.user_id)
    history = (await session.execute(stmt)).scalar_one_or_none()

    if history is None:
        history = GenerationHistory(
            user_id=job.user_id,
            generation_job_id=job.id,
            prompt=job.prompt,
            locale=job.locale,
            status=job.status,
            ide_config=job.ide_config,
            error=job.error,
        )
        session.add(history)
    else:
        history.generation_job_id = job.id
        history.prompt = job.prompt
        history.locale = job.locale
        history.status = job.status
        history.ide_config = job.ide_config
        history.error = job.error

    await session.commit()
