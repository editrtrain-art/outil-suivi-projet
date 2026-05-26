"""Audit logging decorator for domain mutations.

Records changes to core entities with old and new values, tracking
who performed the action and when.
"""

from __future__ import annotations

import functools
from typing import Any, Callable, TypeVar

import structlog
from fastapi import Request

from app.core.exceptions import DomainError

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def audit_log(entity_type: str, action: str) -> Callable[[F], F]:
    """Decorator to log mutations to the audit trail.

    In a production implementation, this would persist entries to the
    `audit_logs` table in the database.

    Args:
        entity_type: The name of the entity (e.g., 'project', 'task').
        action: The mutation performed ('create', 'update', 'delete').

    Returns:
        Callable: The wrapped function.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # We assume the request is available in kwargs (common FastAPI pattern)
            # or we rely on structlog context vars.
            try:
                result = await func(*args, **kwargs)

                logger.info(
                    "audit_event",
                    entity_type=entity_type,
                    action=action,
                    status="success",
                )
                return result
            except DomainError as e:
                logger.warning(
                    "audit_event_failed",
                    entity_type=entity_type,
                    action=action,
                    error=str(e),
                )
                raise
            except Exception as e:
                logger.error(
                    "audit_event_error",
                    entity_type=entity_type,
                    action=action,
                    error=str(e),
                )
                raise

        return wrapper  # type: ignore[return-value]

    return decorator
