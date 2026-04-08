"""init schema

Revision ID: 0001_init
Revises:
Create Date: 2026-04-08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0001_init"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    generation_status = sa.Enum("queued", "running", "succeeded", "failed", name="generation_status")
    generation_status_history = sa.Enum(
        "queued", "running", "succeeded", "failed", name="generation_status_history"
    )

    op.create_table(
        "generation_jobs",
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("locale", sa.String(length=5), nullable=False),
        sa.Column("status", generation_status, nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("ide_config", sa.JSON(), nullable=True),
        sa.Column("error", sa.JSON(), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_generation_jobs"),
    )
    op.create_index("ix_generation_jobs_status", "generation_jobs", ["status"], unique=False)
    op.create_index("ix_generation_jobs_user_created", "generation_jobs", ["user_id", "created_at"], unique=False)
    op.create_index("ix_generation_jobs_user_id", "generation_jobs", ["user_id"], unique=False)

    op.create_table(
        "generation_history",
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("generation_job_id", sa.String(), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("locale", sa.String(length=5), nullable=False),
        sa.Column("status", generation_status_history, nullable=False),
        sa.Column("ide_config", sa.JSON(), nullable=True),
        sa.Column("error", sa.JSON(), nullable=True),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["generation_job_id"],
            ["generation_jobs.id"],
            name="fk_generation_history_generation_job_id_generation_jobs",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_generation_history"),
        sa.UniqueConstraint("generation_job_id", name="uq_generation_history_generation_job_id"),
        sa.UniqueConstraint("user_id", name="uq_generation_history_user_id"),
    )
    op.create_index("ix_generation_history_user_id", "generation_history", ["user_id"], unique=True)

    op.create_table(
        "ide_profiles",
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("ide_config", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_ide_profiles"),
    )
    op.create_index("ix_ide_profiles_user_id", "ide_profiles", ["user_id"], unique=False)
    op.create_index("ix_ide_profiles_user_name", "ide_profiles", ["user_id", "name"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ide_profiles_user_name", table_name="ide_profiles")
    op.drop_index("ix_ide_profiles_user_id", table_name="ide_profiles")
    op.drop_table("ide_profiles")

    op.drop_index("ix_generation_history_user_id", table_name="generation_history")
    op.drop_table("generation_history")

    op.drop_index("ix_generation_jobs_user_id", table_name="generation_jobs")
    op.drop_index("ix_generation_jobs_user_created", table_name="generation_jobs")
    op.drop_index("ix_generation_jobs_status", table_name="generation_jobs")
    op.drop_table("generation_jobs")

    sa.Enum(name="generation_status_history").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="generation_status").drop(op.get_bind(), checkfirst=True)
