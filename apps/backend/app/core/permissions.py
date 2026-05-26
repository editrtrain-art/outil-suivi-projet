"""FastAPI dependencies for Role-Based Access Control (RBAC).

Provides guards to ensure the current user has the required role
within a workspace, per master-guidelines Annex C.

Roles hierarchy (most → least privileged):
    admin > pm > contributor > viewer
"""

from __future__ import annotations

from typing import Any

from fastapi import Depends

from app.core.dependencies import get_current_user
from app.core.exceptions import ForbiddenError


def require_role(allowed_roles: list[str]) -> Any:
    """FastAPI dependency to enforce role membership.

    Args:
        allowed_roles: List of role strings (e.g., ["admin", "pm"]).

    Returns:
        Callable: A dependency function that validates and returns the user.
    """

    async def role_checker(
        current_user: dict[str, Any] = Depends(get_current_user),
    ) -> dict[str, Any]:
        """Verify the current user's role is in the allowed set.

        Raises:
            ForbiddenError: If user role is not in allowed_roles.
        """
        user_role = current_user.get("role", "viewer")
        if user_role not in allowed_roles:
            raise ForbiddenError(
                action=f"access requiring one of {allowed_roles}"
            )
        return current_user

    return role_checker


# ── Convenience dependencies per master-guidelines Annex C ────────────────────

async def require_viewer(
    current_user: dict[str, Any] = Depends(
        require_role(["admin", "pm", "contributor", "viewer"])
    ),
) -> dict[str, Any]:
    """Any authenticated workspace member can access (read-only endpoints)."""
    return current_user


async def require_contributor(
    current_user: dict[str, Any] = Depends(
        require_role(["admin", "pm", "contributor"])
    ),
) -> dict[str, Any]:
    """Contributor or higher — can enter progress logs, submit deliverables."""
    return current_user


async def require_pm(
    current_user: dict[str, Any] = Depends(
        require_role(["admin", "pm"])
    ),
) -> dict[str, Any]:
    """PM or Admin — can create/edit tasks, lock baselines, manage risks."""
    return current_user


async def require_admin(
    current_user: dict[str, Any] = Depends(
        require_role(["admin"])
    ),
) -> dict[str, Any]:
    """Admin only — can manage workspace members, delete projects."""
    return current_user
