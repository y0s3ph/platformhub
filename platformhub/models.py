"""SQLAlchemy ORM models."""

from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from platformhub.database import Base


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


class Role(str, enum.Enum):
    DEVELOPER = "developer"
    APPROVER = "approver"
    ADMIN = "admin"


class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ResourceType(str, enum.Enum):
    K8S_NAMESPACE = "k8s_namespace"
    S3_BUCKET = "s3_bucket"
    RDS_DATABASE = "rds_database"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.DEVELOPER)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    requests: Mapped[list[ResourceRequest]] = relationship(
        back_populates="requester", foreign_keys="ResourceRequest.requester_id"
    )


class ResourceRequest(Base):
    __tablename__ = "resource_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    resource_type: Mapped[ResourceType] = mapped_column(Enum(ResourceType))
    name: Mapped[str] = mapped_column(String(100))
    environment: Mapped[str] = mapped_column(String(20))
    parameters: Mapped[str] = mapped_column(Text, default="{}")
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus), default=RequestStatus.PENDING
    )
    generated_manifest: Mapped[str | None] = mapped_column(Text, nullable=True)

    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    review_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    requester: Mapped[User] = relationship(back_populates="requests", foreign_keys=[requester_id])
    reviewer: Mapped[User | None] = relationship(foreign_keys=[reviewer_id])
    audit_logs: Mapped[list[AuditLog]] = relationship(back_populates="request")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("resource_requests.id"))
    action: Mapped[str] = mapped_column(String(50))
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    request: Mapped[ResourceRequest] = relationship(back_populates="audit_logs")
    actor: Mapped[User] = relationship()
