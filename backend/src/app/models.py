from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ClientModel(Base):
    __tablename__ = "clients"
    client_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FilmModel(Base):
    __tablename__ = "films"
    film_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    client_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("clients.client_id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    source_language: Mapped[str] = mapped_column(String(20), nullable=False)
    target_languages: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FilmEnvironmentModel(Base):
    __tablename__ = "film_environments"
    environment_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    film_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("films.film_id"), nullable=False, unique=True)
    provider: Mapped[str] = mapped_column(String(16), nullable=False, default="aws")
    aws_account_id: Mapped[str] = mapped_column(String(20), nullable=False)
    aws_region: Mapped[str] = mapped_column(String(32), nullable=False)
    subdomain: Mapped[str] = mapped_column(String(63), nullable=False, unique=True)
    terraform_state_key: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="provisioning")
    runtime_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DeploymentModel(Base):
    __tablename__ = "deployments"
    deployment_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    environment_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("film_environments.environment_id"), nullable=False)
    version: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class JobModel(Base):
    __tablename__ = "jobs"
    job_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    film_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("films.film_id"), nullable=False)
    environment_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("film_environments.environment_id"), nullable=False)
    job_type: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="queued")
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditEventModel(Base):
    __tablename__ = "audit_events"
    event_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    actor_id: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    outcome: Mapped[str] = mapped_column(String(16), nullable=False)
    client_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    film_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    environment_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
