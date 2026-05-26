"""Project service implementation.

Handles project lifecycle and statistics.
"""

from __future__ import annotations

import uuid
from typing import List

from app.domain.models.project import Project
from app.core.exceptions import NotFoundError
from app.domain.repositories.interfaces import IProjectRepository


from sqlalchemy.ext.asyncio import AsyncSession

class ProjectService:
    def __init__(self, project_repo: IProjectRepository | AsyncSession) -> None:
        if isinstance(project_repo, AsyncSession):
            from app.infrastructure.repositories.sqlalchemy_repos import SQLAlchemyProjectRepository
            self.project_repo = SQLAlchemyProjectRepository(project_repo)
        else:
            self.project_repo = project_repo

    async def create_project(self, workspace_id: uuid.UUID, **kwargs) -> Project:
        project = Project(workspace_id=workspace_id, **kwargs)
        await self.project_repo.add(project)
        await self.project_repo.commit()
        await self.project_repo.refresh(project)
        return project

    async def get_project_by_id(self, project_id: uuid.UUID) -> Project:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project", project_id)
        return project

    async def get_workspace_projects(self, workspace_id: uuid.UUID) -> List[Project]:
        return await self.project_repo.get_workspace_projects(workspace_id)

    async def update_project(self, project_id: uuid.UUID, **kwargs) -> Project:
        project = await self.get_project_by_id(project_id)
        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)
        await self.project_repo.commit()
        await self.project_repo.refresh(project)
        return project

    async def get_project_stats(self, project_id: uuid.UUID) -> dict:
        project = await self.get_project_by_id(project_id)
        # This is a placeholder for actual aggregation logic
        return {
            "id": project.id,
            "name": project.name,
            "status": project.status,
            "tasks_count": 0,  # TODO: Implement actual counts
            "deliverables_count": 0,
            "resources_count": 0
        }
