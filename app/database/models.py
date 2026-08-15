from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    url: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        unique=True
    )

    resource_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    relevance_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    educational_quality: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    credibility: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    learning_effectiveness: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    overall_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )