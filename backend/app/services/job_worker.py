import asyncio
from contextlib import suppress

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.core.logging import log_event
from app.models.generation import GenerationJob
from app.services.history import upsert_history
from app.services.ide_generation import generate_ide_config


async def worker_loop(settings: Settings, session_maker: async_sessionmaker[AsyncSession]) -> None:
    while True:
        try:
            async with session_maker() as session:
                job = await _next_queued_job(session)
                if not job:
                    await asyncio.sleep(settings.worker_poll_interval_seconds)
                    continue

                job.status = "running"
                job.progress = 20
                await session.commit()
                await session.refresh(job)

                try:
                    ide_config = await generate_ide_config(job.prompt, job.locale, settings)
                    job.ide_config = ide_config.model_dump(mode="json")
                    job.status = "succeeded"
                    job.progress = 100
                    job.error = None
                except Exception as exc:  # pragma: no cover - defensive guard
                    job.status = "failed"
                    job.progress = 100
                    job.error = {"code": "generation_failed", "message": str(exc)}

                await session.commit()
                await session.refresh(job)
                await upsert_history(session, job)

                log_event(
                    "generation_job_finished",
                    generation_id=job.id,
                    user_id=job.user_id,
                    status=job.status,
                )
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # pragma: no cover - keep worker alive
            log_event("worker_error", error=str(exc))
            await asyncio.sleep(settings.worker_poll_interval_seconds)


async def _next_queued_job(session: AsyncSession) -> GenerationJob | None:
    stmt = (
        select(GenerationJob)
        .where(GenerationJob.status == "queued")
        .order_by(GenerationJob.created_at.asc())
        .limit(1)
    )
    return (await session.execute(stmt)).scalar_one_or_none()


def stop_worker(task: asyncio.Task | None) -> None:
    if task is None:
        return
    task.cancel()
    with suppress(asyncio.CancelledError):
        pass
