"""Workspace service implementation.

Handles business logic for workspace lifecycle.
"""

from __future__ import annotations

import uuid
from typing import List

from app.domain.models.workspace import Workspace
from app.domain.models.workspace_member import WorkspaceMember
from app.core.exceptions import NotFoundError, ConflictError
from app.domain.repositories.interfaces import IWorkspaceRepository


from sqlalchemy.ext.asyncio import AsyncSession

class WorkspaceService:
    def __init__(self, workspace_repo: IWorkspaceRepository | AsyncSession) -> None:
        if isinstance(workspace_repo, AsyncSession):
            from app.infrastructure.repositories.sqlalchemy_repos import SQLAlchemyWorkspaceRepository
            self.workspace_repo = SQLAlchemyWorkspaceRepository(workspace_repo)
        else:
            self.workspace_repo = workspace_repo

    async def create_workspace(self, name: str, slug: str, creator_id: uuid.UUID) -> Workspace:
        # Check if slug exists
        existing = await self.workspace_repo.get_by_slug(slug)
        if existing:
            raise ConflictError(f"Workspace slug '{slug}' is already taken.")

        workspace = Workspace(
            name=name,
            slug=slug,
            created_by=creator_id,
            plan_type="free",
            settings={}
        )
        await self.workspace_repo.add(workspace)
        await self.workspace_repo.flush()

        # Add creator as Admin
        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=creator_id,
            role="admin"
        )
        await self.workspace_repo.add_member(member)
        await self.workspace_repo.commit()
        await self.workspace_repo.refresh(workspace)
        return workspace

    async def get_workspace_by_id(self, workspace_id: uuid.UUID) -> Workspace:
        workspace = await self.workspace_repo.get_by_id(workspace_id)
        if not workspace:
            raise NotFoundError("Workspace", workspace_id)
        return workspace

    async def get_user_workspaces(self, user_id: uuid.UUID) -> List[Workspace]:
        return await self.workspace_repo.get_user_workspaces(user_id)

    async def update_workspace(self, workspace_id: uuid.UUID, **kwargs) -> Workspace:
        workspace = await self.get_workspace_by_id(workspace_id)
        for key, value in kwargs.items():
            if hasattr(workspace, key):
                setattr(workspace, key, value)
        await self.workspace_repo.commit()
        await self.workspace_repo.refresh(workspace)
        return workspace

    async def delete_workspace(self, workspace_id: uuid.UUID) -> None:
        workspace = await self.get_workspace_by_id(workspace_id)
        await self.workspace_repo.delete(workspace)
        await self.workspace_repo.commit()
