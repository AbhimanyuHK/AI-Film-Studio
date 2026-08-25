from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class AssetBase(DeclarativeBase):
    pass


class AssetModel(AssetBase):
    __tablename__ = "assets"
    __table_args__ = (UniqueConstraint("film_id", "object_key", name="uq_asset_film_object_key"),)

    asset_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    film_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("films.film_id"), nullable=False)
    environment_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("film_environments.environment_id"), nullable=False)
    object_key: Mapped[str] = mapped_column(Text, nullable=False)
    asset_type: Mapped[str] = mapped_column(String(64), nullable=False)
    content_type: Mapped[str] = mapped_column(String(255), nullable=False)
    size_bytes: Mapped[int | None] = mapped_column(nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(128), nullable=True)
    version: Mapped[int] = mapped_column(nullable=False, default=1)
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
