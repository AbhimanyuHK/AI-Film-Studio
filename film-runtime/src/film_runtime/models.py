from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class FilmMetadata(Base):
    __tablename__ = 'film_metadata'
    film_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(32), default='draft')
    metadata_json: Mapped[dict] = mapped_column('metadata', JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Character(Base):
    __tablename__ = 'characters'
    character_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(300))
    description: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column('metadata', JSON, default=dict)


class Scene(Base):
    __tablename__ = 'scenes'
    scene_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    scene_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict] = mapped_column('metadata', JSON, default=dict)
    shots: Mapped[list['Shot']] = relationship(cascade='all, delete-orphan')


class Shot(Base):
    __tablename__ = 'shots'
    shot_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    scene_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('scenes.scene_id', ondelete='CASCADE'))
    shot_number: Mapped[int] = mapped_column(Integer)
    prompt: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default='planned')
    metadata_json: Mapped[dict] = mapped_column('metadata', JSON, default=dict)


class ProductionJob(Base):
    __tablename__ = 'production_jobs'
    job_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    operation: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default='queued')
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    result: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FilmAsset(Base):
    __tablename__ = 'film_assets'
    asset_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    asset_type: Mapped[str] = mapped_column(String(64))
    object_key: Mapped[str] = mapped_column(String(2048))
    content_type: Mapped[str | None] = mapped_column(String(128))
    checksum: Mapped[str | None] = mapped_column(String(256))
    metadata_json: Mapped[dict] = mapped_column('metadata', JSON, default=dict)
