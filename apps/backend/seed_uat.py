"""UAT Seeding Script for NEXUS V3.

Simulates a real user workflow:
1. Creates a Workspace.
2. Creates a Project with Phase and Tasks.
3. Establishes dependencies.
4. Triggers CPM engine.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_factory
from app.domain.services.workspace_service import WorkspaceService
from app.domain.services.project_service import ProjectService
from app.domain.services.phase_service import PhaseService
from app.domain.services.task_service import TaskService
from app.domain.models.user import User

async def run_uat():
    async with async_session_factory() as db:
        # 0. Ensure a test user exists (Deterministic UUID from 'uat-user')
        user_id = uuid.uuid5(uuid.NAMESPACE_DNS, "uat-user")
        user = await db.get(User, user_id)
        if not user:
            user = User(
                id=user_id,
                email="uat@nexus.ai",
                first_name="UAT",
                last_name="Tester",
                role_global="admin"
            )
            db.add(user)
            await db.commit()
            print(f"✅ User created: {user.email}")

        from app.infrastructure.repositories.sqlalchemy_repos import (
            SQLAlchemyWorkspaceRepository,
            SQLAlchemyProjectRepository,
            SQLAlchemyPhaseRepository,
            SQLAlchemyTaskRepository,
        )
        workspace_service = WorkspaceService(SQLAlchemyWorkspaceRepository(db))
        project_service = ProjectService(SQLAlchemyProjectRepository(db))
        phase_service = PhaseService(SQLAlchemyPhaseRepository(db))
        task_service = TaskService(SQLAlchemyTaskRepository(db), SQLAlchemyPhaseRepository(db), SQLAlchemyProjectRepository(db))

        # 1. Create Workspace
        try:
            ws = await workspace_service.create_workspace(
                name="JESA NEXUS UAT",
                slug=f"jesa-uat-{uuid.uuid4().hex[:4]}",
                creator_id=user_id
            )
            print(f"✅ Workspace created: {ws.name}")
        except Exception as e:
            print(f"⚠️ Workspace creation skipped: {e}")
            return

        # 2. Create Project
        proj = await project_service.create_project(
            workspace_id=ws.id,
            name="Plant Construction V3",
            description="End-to-end industrial project control simulation.",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            budget_total=5000000.0,
            pm_user_id=user_id
        )
        print(f"✅ Project created: {proj.name}")

        # 3. Create Phase
        phase = await phase_service.create_phase(
            project_id=proj.id,
            name="Foundations & Civil",
            weight_percent=20.0
        )
        print(f"✅ Phase created: {phase.name}")

        # 4. Create Tasks
        t1 = await task_service.create_task(
            phase_id=phase.id,
            name="Site Clearing",
            duration_days=5
        )
        t2 = await task_service.create_task(
            phase_id=phase.id,
            name="Excavation",
            duration_days=10
        )
        t3 = await task_service.create_task(
            phase_id=phase.id,
            name="Concrete Pouring",
            duration_days=15
        )
        print(f"✅ 3 Tasks created.")

        # 5. Add Dependencies (T1 -> T2 -> T3)
        await task_service.add_dependency(t2.id, t1.id, dep_type="FS")
        await task_service.add_dependency(t3.id, t2.id, dep_type="FS", lag_days=2)
        print(f"✅ Dependencies established (FS + Lag).")

        # 6. Run CPM
        await task_service.run_cpm_for_project(proj.id)
        print(f"🚀 CPM Engine execution completed successfully.")
        
        # Verify results
        await db.refresh(t3)
        print(f"📊 Task '{t3.name}' Scheduled Finish: {t3.end_date_scheduled}")
        print(f"📊 Task '{t3.name}' Is Critical: {t3.is_critical}")

if __name__ == "__main__":
    asyncio.run(run_uat())
