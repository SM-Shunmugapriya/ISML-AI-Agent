from datetime import datetime

from sqlalchemy import (
    DateTime, Float, ForeignKey, Integer, String, Text, func
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from pgvector.sqlalchemy import Vector

from app.database.database import Base


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False, unique=True)
    content_hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    educational_quality: Mapped[float | None] = mapped_column(Float, nullable=True)
    credibility: Mapped[float | None] = mapped_column(Float, nullable=True)
    learning_effectiveness: Mapped[float | None] = mapped_column(Float, nullable=True)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(3072), nullable=True
    )

    processing_status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False
    )

    # ENH-010: Resource lifecycle status
    status: Mapped[str] = mapped_column(
        String(20),
        default="DISCOVERED",
        server_default="DISCOVERED",
        nullable=False
    )

    # ENH-011: Resource creation timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # ENH-011: Resource update timestamp
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now(),
        nullable=False
    )

    # ENH-011: Last verification timestamp
    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    # ENH-011: unknown, available, unavailable
    availability_status: Mapped[str] = mapped_column(
        String(20),
        default="unknown",
        server_default="unknown",
        nullable=False
    )


# ENH-010: Track resource lifecycle status changes
class ResourceLifecycleEvent(Base):
    __tablename__ = "resource_lifecycle_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    resource_id: Mapped[int] = mapped_column(
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    from_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    to_status: Mapped[str] = mapped_column(String(20), nullable=False)

    changed_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    note: Mapped[str | None] = mapped_column(Text, nullable=True)
