"""Resource service implementation.

Handles resource lifecycle and availability.
"""

from __future__ import annotations

import uuid
from typing import List

from app.domain.models.resource import Resource
from app.core.exceptions import NotFoundError
from app.domain.repositories.interfaces import IResourceRepository


from sqlalchemy.ext.asyncio import AsyncSession

class ResourceService:
    def __init__(self, resource_repo: IResourceRepository | AsyncSession) -> None:
        if isinstance(resource_repo, AsyncSession):
            from app.infrastructure.repositories.sqlalchemy_repos import SQLAlchemyResourceRepository
            self.resource_repo = SQLAlchemyResourceRepository(resource_repo)
        else:
            self.resource_repo = resource_repo

    async def create_resource(self, workspace_id: uuid.UUID, name: str, role: str, hourly_rate: float) -> Resource:
        resource = Resource(
            workspace_id=workspace_id,
            name=name,
            role=role,
            hourly_rate_dh=hourly_rate,
            is_active=True
        )
        await self.resource_repo.add(resource)
        await self.resource_repo.commit()
        await self.resource_repo.refresh(resource)
        return resource

    async def get_workspace_resources(self, workspace_id: uuid.UUID) -> List[Resource]:
        return await self.resource_repo.get_workspace_resources(workspace_id)

    async def get_resource_by_id(self, resource_id: uuid.UUID) -> Resource:
        resource = await self.resource_repo.get_by_id(resource_id)
        if not resource:
            raise NotFoundError("Resource", resource_id)
        return resource
