from __future__ import annotations

import uuid
from datetime import date, timedelta
from typing import Dict, List, Any, Set
import structlog
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.task import Task
from app.domain.models.phase import Phase
from app.domain.models.task_dependency import TaskDependency
from app.domain.models.task_assignment import TaskAssignment
from app.domain.models.resource import Resource
from app.domain.services.task_service import TaskService
from app.core.exceptions import NotFoundError

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class ResourceLevelerService:
    """Service implementing resource load computation, smoothing, and leveling."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_daily_load(self, project_id: uuid.UUID) -> Dict[str, Any]:
        """Compute the daily resource allocation profile for a project.

        Args:
            project_id: UUID of the project.

        Returns:
            Dict[str, Any]: Timeline dates and daily load profiles for each resource.
        """
        # Load tasks with assignments and resource info
        result = await self.db.execute(
            select(Task)
            .join(Phase, Task.phase_id == Phase.id)
            .where(Phase.project_id == project_id)
            .options(selectinload(Task.assignments).selectinload(TaskAssignment.resource))
        )
        tasks = result.scalars().all()

        if not tasks:
            return {"timeline": [], "resources": {}}

        # Find project boundaries
        start_dates = [t.start_date_scheduled for t in tasks if t.start_date_scheduled]
        end_dates = [t.end_date_scheduled for t in tasks if t.end_date_scheduled]

        if not start_dates or not end_dates:
            return {"timeline": [], "resources": {}}

        proj_start = min(start_dates)
        proj_end = max(end_dates)

        total_days = (proj_end - proj_start).days + 1
        timeline = [str(proj_start + timedelta(days=d)) for d in range(total_days)]

        # Map of resource ID -> details + daily load profile
        load_profile: Dict[str, Dict[str, Any]] = {}

        for t in tasks:
            if not t.start_date_scheduled or not t.end_date_scheduled:
                continue
            t_start = t.start_date_scheduled
            t_end = t.end_date_scheduled

            for assignment in t.assignments:
                res = assignment.resource
                if not res:
                    continue
                res_id_str = str(res.id)
                if res_id_str not in load_profile:
                    capacity = res.monthly_capacity_hours / 168.0 * 100.0 if res.monthly_capacity_hours else 100.0
                    load_profile[res_id_str] = {
                        "name": res.name,
                        "role": res.role,
                        "capacity": round(capacity, 1),
                        "daily_allocations": [0.0] * total_days,
                    }

                # Update daily load values
                for d in range(total_days):
                    current_date = proj_start + timedelta(days=d)
                    if t_start <= current_date <= t_end:
                        load_profile[res_id_str]["daily_allocations"][d] += float(assignment.allocation_percent or 100.0)

        # Round allocations
        for res_id in load_profile:
            load_profile[res_id]["daily_allocations"] = [
                round(val, 1) for val in load_profile[res_id]["daily_allocations"]
            ]

        return {"timeline": timeline, "resources": load_profile}

    async def smooth_resources(self, project_id: uuid.UUID) -> None:
        """Resource Smoothing Heuristic.

        Shifts task schedules strictly within their calculated float bounds (total_float)
        to minimize resource demand fluctuations (load variance) without extending the project end date.

        Args:
            project_id: UUID of the project.
        """
        # Load tasks
        result = await self.db.execute(
            select(Task)
            .join(Phase, Task.phase_id == Phase.id)
            .where(Phase.project_id == project_id)
            .options(
                selectinload(Task.assignments).selectinload(TaskAssignment.resource),
                selectinload(Task.dependencies)
            )
        )
        tasks = list(result.scalars().all())

        if not tasks:
            return

        # Sort tasks by float descending (shift tasks with most flexibility first)
        flexible_tasks = [t for t in tasks if t.total_float > 0 and t.assignments]
        flexible_tasks.sort(key=lambda x: x.total_float, reverse=True)

        for task in flexible_tasks:
            if not task.start_date_scheduled or not task.early_start or not task.late_start:
                continue

            max_shift_days = (task.late_start - task.early_start).days
            if max_shift_days <= 0:
                continue

            best_shift = 0
            best_variance = float("inf")
            duration = task.duration_days or 1

            # Iterate through possible shifts inside CPM float window
            for shift in range(max_shift_days + 1):
                temp_start = task.early_start + timedelta(days=shift)
                temp_end = temp_start + timedelta(days=duration)

                # Temporarily apply schedule shift
                orig_start = task.start_date_scheduled
                orig_end = task.end_date_scheduled
                task.start_date_scheduled = temp_start
                task.end_date_scheduled = temp_end
                await self.db.flush()

                # Calculate resource profile variance
                load = await self.get_daily_load(project_id)
                variance = self._calculate_profile_variance(load["resources"])

                if variance < best_variance:
                    best_variance = variance
                    best_shift = shift

                # Revert shift
                task.start_date_scheduled = orig_start
                task.end_date_scheduled = orig_end
                await self.db.flush()

            # Apply optimal shift
            opt_start = task.early_start + timedelta(days=best_shift)
            task.start_date_scheduled = opt_start
            task.end_date_scheduled = opt_start + timedelta(days=duration)
            self.db.add(task)

        await self.db.commit()

        # Re-run CPM to update new float values
        task_service = TaskService(self.db)
        await task_service.run_cpm_for_project(project_id)

    async def level_resources(self, project_id: uuid.UUID) -> None:
        """Resource Leveling Engine (Resource-Constrained Heuristic).

        Resolves resource over-allocations (daily load > capacity) by delaying tasks.
        Can push schedules past floats and extend the project end date.

        Args:
            project_id: UUID of the project.
        """
        # Load tasks
        result = await self.db.execute(
            select(Task)
            .join(Phase, Task.phase_id == Phase.id)
            .where(Phase.project_id == project_id)
            .options(
                selectinload(Task.assignments).selectinload(TaskAssignment.resource),
                selectinload(Task.dependencies)
            )
        )
        tasks = list(result.scalars().all())

        if not tasks:
            return

        # Simple Day-by-Day Serial Associative Leveling
        start_dates = [t.start_date_scheduled for t in tasks if t.start_date_scheduled]
        end_dates = [t.end_date_scheduled for t in tasks if t.end_date_scheduled]
        if not start_dates or not end_dates:
            return

        proj_start = min(start_dates)
        proj_end = max(end_dates)
        
        max_leveling_days = 365 # guard rail (1 year max extension)
        current_date = proj_start
        days_offset = 0

        while current_date <= proj_end and days_offset < max_leveling_days:
            # Check resource load on this specific day
            load = await self.get_daily_load(project_id)
            overallocated_resources = []
            
            for res_id, res_load in load["resources"].items():
                allocations = res_load["daily_allocations"]
                if days_offset < len(allocations):
                    day_load = allocations[days_offset]
                    capacity = res_load["capacity"]
                    if day_load > capacity:
                        overallocated_resources.append(res_id)

            if overallocated_resources:
                # Find active tasks on this day using any overallocated resource
                active_tasks = []
                for t in tasks:
                    if t.start_date_scheduled and t.end_date_scheduled:
                        if t.start_date_scheduled <= current_date <= t.end_date_scheduled:
                            has_overload_res = any(
                                str(assign.resource_id) in overallocated_resources
                                for assign in t.assignments
                            )
                            if has_overload_res:
                                active_tasks.append(t)

                # Sort tasks: lower float (critical) or higher priority remains; higher float / lower priority delayed
                # (Priority 1 = Highest, 5 = Lowest)
                active_tasks.sort(key=lambda x: (x.total_float, -x.priority))

                # Keep tasks up to capacity limits, push others by 1 day
                resource_tallies: Dict[str, float] = {r: 0.0 for r in overallocated_resources}
                for t in active_tasks:
                    can_schedule = True
                    for assign in t.assignments:
                        res_id_str = str(assign.resource_id)
                        if res_id_str in resource_tallies:
                            capacity = next(
                                r["capacity"] for r in load["resources"].values()
                                if r["name"] == assign.resource.name
                            )
                            tally = resource_tallies[res_id_str] + float(assign.allocation_percent or 100.0)
                            if tally > capacity:
                                can_schedule = False
                                break

                    if not can_schedule:
                        # Delay task to start tomorrow
                        logger.info("leveling_delay_task", task_name=t.name, date=str(current_date))
                        tomorrow = current_date + timedelta(days=1)
                        await self.cascade_delay(t, tomorrow)
                        
                        # Refresh project end boundary if extended
                        end_dates = [tk.end_date_scheduled for tk in tasks if tk.end_date_scheduled]
                        proj_end = max(end_dates)
                    else:
                        # Log allocated resources
                        for assign in t.assignments:
                            res_id_str = str(assign.resource_id)
                            if res_id_str in resource_tallies:
                                resource_tallies[res_id_str] += float(assign.allocation_percent or 100.0)

            # Move to next day
            days_offset += 1
            current_date = proj_start + timedelta(days=days_offset)

        await self.db.commit()

        # Re-run CPM to sync final floats and paths
        task_service = TaskService(self.db)
        await task_service.run_cpm_for_project(project_id)

    async def cascade_delay(self, task: Task, new_start: date) -> None:
        """Cascades scheduled delays down dependency chains recursively.

        Args:
            task: Task object to delay.
            new_start: Target start date.
        """
        if not task.start_date_scheduled or new_start <= task.start_date_scheduled:
            return

        duration = task.duration_days or 1
        task.start_date_scheduled = new_start
        task.end_date_scheduled = new_start + timedelta(days=duration)
        self.db.add(task)
        await self.db.flush()

        # Find successor tasks
        result = await self.db.execute(
            select(Task)
            .join(TaskDependency, Task.id == TaskDependency.task_id)
            .where(TaskDependency.predecessor_task_id == task.id)
            .options(selectinload(Task.dependencies))
        )
        successors = result.scalars().all()

        for succ in successors:
            dep_link = next(
                d for d in succ.dependencies
                if d.predecessor_task_id == task.id
            )
            lag = dep_link.lag_days or 0
            
            # Compute new successor start date based on dependency type
            if dep_link.dependency_type == "FS":
                # Finish-to-Start: Succ starts after pred ends
                target_start = task.end_date_scheduled + timedelta(days=lag)
            elif dep_link.dependency_type == "SS":
                # Start-to-Start: Succ starts after pred starts
                target_start = task.start_date_scheduled + timedelta(days=lag)
            elif dep_link.dependency_type == "FF":
                # Finish-to-Finish: Succ ends after pred ends
                target_end = task.end_date_scheduled + timedelta(days=lag)
                target_start = target_end - timedelta(days=succ.duration_days or 1)
            elif dep_link.dependency_type == "SF":
                # Start-to-Finish: Succ ends after pred starts
                target_end = task.start_date_scheduled + timedelta(days=lag)
                target_start = target_end - timedelta(days=succ.duration_days or 1)
            else:
                target_start = task.end_date_scheduled

            if succ.start_date_scheduled and target_start > succ.start_date_scheduled:
                await self.cascade_delay(succ, target_start)

    def _calculate_profile_variance(self, resources_load: Dict[str, Dict[str, Any]]) -> float:
        """Helper to calculate resource allocation variance sum."""
        total_variance = 0.0
        for r_id in resources_load:
            allocs = resources_load[r_id]["daily_allocations"]
            if not allocs:
                continue
            mean = sum(allocs) / len(allocs)
            variance = sum((x - mean) ** 2 for x in allocs) / len(allocs)
            total_variance += variance
        return total_variance
