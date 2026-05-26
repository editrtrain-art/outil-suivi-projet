# Implementation Plan — Backend Service Instantiation & Repository Fixes

Before deploying to Vercel, we need to address several critical service instantiation errors and missing repository methods that cause API routes to crash and unit tests to fail.

## User Review Required

> [!IMPORTANT]
> The backend tests are currently failing because `TaskService`, `NotificationService`, and `ResourceService` are being instantiated directly using database sessions (`AsyncSession`) instead of their respective repositories (`IRepository`).
> We will fix these occurrences by:
> 1. Updating routers to use FastAPI's dependency injection (`Depends(get_task_service)`, etc.) which correctly wires repositories.
> 2. Manually instantiating the repositories inside domain services (like `resource_leveler.py` and `risk_service.py`) that do not run inside FastAPI's request-response cycle.
> 3. Adding missing `get_phase_tasks` and `get_project_tasks` methods to the `ITaskRepository` interface and its SQLAlchemy implementation.

## Proposed Changes

### 1. Database Repositories Layer

#### [MODIFY] [interfaces.py](file:///c:/Users/Home/Documents/Outil-Suivi-Projet/apps/backend/app/domain/repositories/interfaces.py)
- Add `get_phase_tasks` and `get_project_tasks` signatures to `ITaskRepository`.

#### [MODIFY] [sqlalchemy_repos.py](file:///c:/Users/Home/Documents/Outil-Suivi-Projet/apps/backend/app/infrastructure/repositories/sqlalchemy_repos.py)
- Implement `get_phase_tasks` (ordered by WBS code) and `get_project_tasks` (ordered by WBS code) inside `SQLAlchemyTaskRepository`.

---

### 2. Service Layer

#### [MODIFY] [task_service.py](file:///c:/Users/Home/Documents/Outil-Suivi-Projet/apps/backend/app/domain/services/task_service.py)
- Add `get_phase_tasks` and `get_project_tasks` wrapper methods delegation to `self.task_repo`.

#### [MODIFY] [resource_leveler.py](file:///c:/Users/Home/Documents/Outil-Suivi-Projet/apps/backend/app/domain/services/resource_leveler.py)
- Import `SQLAlchemyTaskRepository`, `SQLAlchemyPhaseRepository`, and `SQLAlchemyProjectRepository`.
- Instantiate `TaskService` with the correct repositories instead of passing `self.db`.

#### [MODIFY] [risk_service.py](file:///c:/Users/Home/Documents/Outil-Suivi-Projet/apps/backend/app/domain/services/risk_service.py)
- Import repositories for `TaskService` and `NotificationService`.
- Instantiate `TaskService` and `NotificationService` with repositories instead of `self.db`.

---

### 3. API Routers Layer

#### [MODIFY] [tasks.py](file:///c:/Users/Home/Documents/Outil-Suivi-Projet/apps/backend/app/routers/tasks.py)
- Import `get_task_service` from `app.core.dependencies`.
- Replace `Depends(get_db)` and `service = TaskService(db)` with `service: TaskService = Depends(get_task_service)` on all endpoints.

#### [MODIFY] [resources.py](file:///c:/Users/Home/Documents/Outil-Suivi-Projet/apps/backend/app/routers/resources.py)
- Import `get_resource_service` from `app.core.dependencies`.
- Replace `Depends(get_db)` and `service = ResourceService(db)` with `service: ResourceService = Depends(get_resource_service)` on all endpoints.

---

### 4. Scripts & Seeders

#### [MODIFY] [seed_uat.py](file:///c:/Users/Home/Documents/Outil-Suivi-Projet/apps/backend/seed_uat.py)
- Instantiate repositories and pass them when creating `WorkspaceService`, `ProjectService`, `PhaseService`, and `TaskService`.

## Verification Plan

### Automated Tests
- Run `pytest` from the backend workspace to ensure all 41 unit and integration tests pass successfully:
  ```powershell
  .venv\Scripts\pytest
  ```
