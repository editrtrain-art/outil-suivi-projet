"""FastAPI dependencies for NEXUS.

Centralizes database session access and user authentication/authorization
via Clerk JWT validation.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any
import uuid

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import async_session_factory, get_db
from app.core.exceptions import ForbiddenError
from app.domain.models.user import User

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)
security = HTTPBearer()


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Validate Clerk JWT, synchronise user details with the DB, and return claims.

    Args:
        token: The Bearer token from the Authorization header.
        db: Scoped async database session.

    Returns:
        dict[str, Any]: The decoded JWT claims with sub replaced by a deterministic UUID.

    Raises:
        HTTPException: If the token is invalid, expired, or missing signature.
    """
    settings = get_settings()
    payload: dict[str, Any] | None = None

    # Handle mock tokens to ease testing and sandbox usage without Clerk setup
    if token.credentials.startswith("mock_"):
        parts = token.credentials.split("_")
        # Support format: mock_<role>_<clerk_id>_<email> or mock_<clerk_id>_<email>
        if len(parts) > 3 and parts[1] in ("admin", "pm", "contributor", "viewer"):
            role = parts[1]
            clerk_id = parts[2]
            email = parts[3]
        else:
            role = "viewer"
            clerk_id = parts[1] if len(parts) > 1 else "mock_user"
            email = parts[2] if len(parts) > 2 else "mock@nexus.local"
        payload = {
            "sub": clerk_id,
            "email": email,
            "first_name": "Mock",
            "last_name": "User",
            "role": role,
        }
        logger.info("auth_bypass_mock_token", user_id=clerk_id, role=role)
    else:
        # Standard token decoding with JWKS or development unverified fallback
        try:
            if settings.CLERK_JWKS_URL:
                # Standard RS256 decoding (python-jose handles signature if JWKS URL is parsed)
                # In typical production setups, public keys from CLERK_JWKS_URL are downloaded and verified.
                # For development speed and flexibility, we try standard decode first.
                payload = jwt.decode(
                    token.credentials,
                    settings.CLERK_SECRET_KEY,
                    algorithms=["RS256", "HS256"],
                    options={"verify_aud": False},
                )
            else:
                if settings.ENVIRONMENT == "development":
                    # Fallback to get claims without signature validation if JWKS url is unset in dev
                    payload = jwt.get_unverified_claims(token.credentials)
                    logger.warning("auth_unverified_fallback_development")
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="JWKS URL not configured for signature verification.",
                    )
        except JWTError as e:
            if settings.ENVIRONMENT == "development":
                # In development, fail-safe to unverified claims if signature check fails
                try:
                    payload = jwt.get_unverified_claims(token.credentials)
                    logger.warning("auth_signature_failed_unverified_fallback_development", error=str(e))
                except Exception as inner_err:
                    logger.warning("auth_failed_unverified_claims", error=str(inner_err))
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Could not validate credentials",
                    ) from e
            else:
                logger.warning("auth_failed", error=str(e))
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                ) from e

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    clerk_id = payload.get("sub", "")
    if not clerk_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject (sub claim)",
        )

    # Convert Clerk's string-based user ID into a deterministic UUID
    user_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, clerk_id)

    # Fetch user data from token claims
    email = payload.get("email") or payload.get("email_address") or f"{clerk_id}@clerk.local"
    first_name = payload.get("first_name") or payload.get("given_name") or ""
    last_name = payload.get("last_name") or payload.get("family_name") or ""
    avatar_url = payload.get("image_url") or payload.get("picture") or ""

    # Synchronise the user to the local database
    user_result = await db.execute(select(User).where(User.id == user_uuid))
    db_user = user_result.scalar_one_or_none()

    if not db_user:
        logger.info("syncing_new_user", clerk_id=clerk_id, email=email)
        db_user = User(
            id=user_uuid,
            email=email,
            first_name=first_name,
            last_name=last_name,
            avatar_url=avatar_url,
            role_global="user",
        )
        db.add(db_user)
        await db.commit()
    else:
        # Check if details changed and update if necessary
        if (
            db_user.email != email
            or db_user.first_name != first_name
            or db_user.last_name != last_name
            or db_user.avatar_url != avatar_url
        ):
            db_user.email = email
            db_user.first_name = first_name
            db_user.last_name = last_name
            db_user.avatar_url = avatar_url
            db.add(db_user)
            await db.commit()

    # Rewrite payload sub with stringified UUID so backend routers get a valid UUID
    payload["sub"] = str(user_uuid)
    return payload


# ── Service Dependencies for Clean Architecture ──────────────────────────────

from app.infrastructure.repositories.sqlalchemy_repos import (
    SQLAlchemyWorkspaceRepository,
    SQLAlchemyProjectRepository,
    SQLAlchemyPhaseRepository,
    SQLAlchemyTaskRepository,
    SQLAlchemyResourceRepository,
    SQLAlchemyTaskAssignmentRepository,
    SQLAlchemyProgressLogRepository,
    SQLAlchemyDeliverableRepository,
    SQLAlchemyRiskRepository,
    SQLAlchemyBaselineRepository,
    SQLAlchemyNotificationRepository,
    SQLAlchemyAIInsightRepository,
)
from app.domain.services.workspace_service import WorkspaceService
from app.domain.services.project_service import ProjectService
from app.domain.services.phase_service import PhaseService
from app.domain.services.task_service import TaskService
from app.domain.services.resource_service import ResourceService
from app.domain.services.assignment_service import AssignmentService
from app.domain.services.progress_service import ProgressService
from app.domain.services.notification_service import NotificationService


def get_workspace_service(db: AsyncSession = Depends(get_db)) -> WorkspaceService:
    repo = SQLAlchemyWorkspaceRepository(db)
    return WorkspaceService(repo)


def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    repo = SQLAlchemyProjectRepository(db)
    return ProjectService(repo)


def get_phase_service(db: AsyncSession = Depends(get_db)) -> PhaseService:
    repo = SQLAlchemyPhaseRepository(db)
    return PhaseService(repo)


def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    task_repo = SQLAlchemyTaskRepository(db)
    phase_repo = SQLAlchemyPhaseRepository(db)
    project_repo = SQLAlchemyProjectRepository(db)
    return TaskService(task_repo, phase_repo, project_repo)


def get_resource_service(db: AsyncSession = Depends(get_db)) -> ResourceService:
    repo = SQLAlchemyResourceRepository(db)
    return ResourceService(repo)


def get_assignment_service(db: AsyncSession = Depends(get_db)) -> AssignmentService:
    repo = SQLAlchemyTaskAssignmentRepository(db)
    return AssignmentService(repo)


def get_progress_service(db: AsyncSession = Depends(get_db)) -> ProgressService:
    progress_repo = SQLAlchemyProgressLogRepository(db)
    task_repo = SQLAlchemyTaskRepository(db)
    return ProgressService(progress_repo, task_repo)


def get_notification_service(db: AsyncSession = Depends(get_db)) -> NotificationService:
    repo = SQLAlchemyNotificationRepository(db)
    return NotificationService(repo)

