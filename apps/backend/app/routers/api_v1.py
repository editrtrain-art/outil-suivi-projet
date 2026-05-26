"""Central API Router V1.

Aggregates all module routers for the V1 API.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.routers.workspaces import router as workspaces_router
from app.routers.projects import router as projects_router
from app.routers.resources import router as resources_router
from app.routers.phases import router as phases_router
from app.routers.tasks import router as tasks_router
from app.routers.evm import router as evm_router
from app.routers.baselines import router as baselines_router
from app.routers.leveling import router as leveling_router
from app.routers.exports import router as exports_router
from app.routers.llm import router as llm_router
from app.routers.deliverables import router as deliverables_router
from app.routers.risks import router as risks_router
from app.routers.notifications import router as notifications_router

router = APIRouter(prefix="/api/v1")

router.include_router(workspaces_router)
router.include_router(projects_router)
router.include_router(resources_router)
router.include_router(phases_router)
router.include_router(tasks_router)
router.include_router(evm_router)
router.include_router(baselines_router)
router.include_router(leveling_router)
router.include_router(exports_router)
router.include_router(llm_router)
router.include_router(deliverables_router)
router.include_router(risks_router)
router.include_router(notifications_router)
