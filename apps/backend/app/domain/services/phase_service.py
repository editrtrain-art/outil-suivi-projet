"""Phase service implementation.

Handles project phases and WBS level 1 ordering.
"""

from __future__ import annotations

import uuid
from typing import List

from app.domain.models.phase import Phase
from app.core.exceptions import NotFoundError
from app.domain.repositories.interfaces import IPhaseRepository


from sqlalchemy.ext.asyncio import AsyncSession

class PhaseService:
    def __init__(self, phase_repo: IPhaseRepository | AsyncSession) -> None:
        if isinstance(phase_repo, AsyncSession):
            from app.infrastructure.repositories.sqlalchemy_repos import SQLAlchemyPhaseRepository
            self.phase_repo = SQLAlchemyPhaseRepository(phase_repo)
        else:
            self.phase_repo = phase_repo

    async def create_phase(self, project_id: uuid.UUID, name: str, weight_percent: float = 0.0) -> Phase:
        # Calculate next order index and WBS code
        count = await self.phase_repo.count_project_phases(project_id)
        order_index = count
        wbs_code = f"{count + 1}.0"

        phase = Phase(
            project_id=project_id,
            name=name,
            wbs_code=wbs_code,
            order_index=order_index,
            weight_percent=weight_percent
        )
        await self.phase_repo.add(phase)
        await self.phase_repo.commit()
        await self.phase_repo.refresh(phase)
        return phase

    async def get_project_phases(self, project_id: uuid.UUID) -> List[Phase]:
        return await self.phase_repo.get_project_phases(project_id)

    async def update_phase(self, phase_id: uuid.UUID, **kwargs) -> Phase:
        phase = await self.phase_repo.get_by_id(phase_id)
        if not phase:
            raise NotFoundError("Phase", phase_id)
        for key, value in kwargs.items():
            if hasattr(phase, key):
                setattr(phase, key, value)
        await self.phase_repo.commit()
        await self.phase_repo.refresh(phase)
        return phase

    async def delete_phase(self, phase_id: uuid.UUID) -> None:
        """Delete a phase and all its tasks (cascades via DB)."""
        phase = await self.phase_repo.get_by_id(phase_id)
        if not phase:
            raise NotFoundError("Phase", str(phase_id))
        await self.phase_repo.delete(phase)
        await self.phase_repo.commit()
