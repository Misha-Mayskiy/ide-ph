from sqlalchemy import JSON, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDTimestampMixin


class IdeProfile(UUIDTimestampMixin, Base):
    __tablename__ = "ide_profiles"

    user_id: Mapped[str] = mapped_column(String(128), index=True)
    name: Mapped[str] = mapped_column(String(120))
    ide_config: Mapped[dict] = mapped_column(JSON)

    __table_args__ = (Index("ix_ide_profiles_user_name", "user_id", "name"),)
