from sqlalchemy import JSON, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDTimestampMixin


GENERATION_STATUS_VALUES = ("queued", "running", "succeeded", "failed")


class GenerationJob(UUIDTimestampMixin, Base):
    __tablename__ = "generation_jobs"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    locale: Mapped[str] = mapped_column(String(5), default="ru")

    status: Mapped[str] = mapped_column(
        Enum(*GENERATION_STATUS_VALUES, name="generation_status"), default="queued", index=True
    )
    progress: Mapped[int] = mapped_column(default=0)

    ide_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (Index("ix_generation_jobs_user_created", "user_id", "created_at"),)


class GenerationHistory(UUIDTimestampMixin, Base):
    __tablename__ = "generation_history"

    user_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    generation_job_id: Mapped[str] = mapped_column(
        ForeignKey("generation_jobs.id", ondelete="CASCADE"), unique=True
    )
    prompt: Mapped[str] = mapped_column(Text)
    locale: Mapped[str] = mapped_column(String(5))
    status: Mapped[str] = mapped_column(
        Enum(*GENERATION_STATUS_VALUES, name="generation_status_history")
    )
    ide_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[dict | None] = mapped_column(JSON, nullable=True)
