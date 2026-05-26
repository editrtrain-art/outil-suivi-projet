"""SQLAlchemy base class and common mixins.

Provides the declarative base and a timestamp mixin for all domain models.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy models."""
    pass


class TimestampMixin:
    """Mixin to add `created_at` and `updated_at` columns to a model."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        sort_order=999,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        sort_order=1000,
    )
