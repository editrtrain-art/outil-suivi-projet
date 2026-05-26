from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import List, Dict, Any, Optional
import httpx
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import NotFoundError
from app.domain.models.project import Project
from app.domain.models.phase import Phase
from app.domain.models.task import Task
from app.domain.models.risk import Risk
from app.domain.models.progress_log import ProgressLog
from app.domain.models.audit_log import AIInsight
from app.domain.services.evm_calculator import EVMCalculator

logger = structlog.get_logger(__name__)


class LLMService:
    """Service to connect with LLM providers (Ollama, OpenAI, Anthropic) and audit projects."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.settings = get_settings()

    async def generate_project_audit(
        self,
        project_id: uuid.UUID,
        triggered_by: Optional[uuid.UUID] = None
    ) -> str:
        """Fetch project data, request risk report from LLM, persist result, and return markdown.

        Args:
            project_id: UUID of the project.
            triggered_by: User UUID who triggered this audit.

        Returns:
            str: Markdown formatted audit report.
        """
        # 1. Load project
        project = await self.db.get(Project, project_id)
        if not project:
            raise NotFoundError("Project", str(project_id))

        # 2. Load phases & tasks
        phases_result = await self.db.execute(
            select(Phase).where(Phase.project_id == project_id)
        )
        phases = phases_result.scalars().all()
        phase_ids = [p.id for p in phases]

        tasks: List[Task] = []
        if phase_ids:
            tasks_result = await self.db.execute(
                select(Task).where(Task.phase_id.in_(phase_ids)).order_by(Task.wbs_code)
            )
            tasks = list(tasks_result.scalars().all())

        # 3. Load risks
        risks_result = await self.db.execute(
            select(Risk).where(Risk.project_id == project_id)
        )
        risks = list(risks_result.scalars().all())

        # 4. Compute EVM
        evm = await self._calculate_evm(project, tasks)

        # 5. Format prompt context
        context_str = self._format_project_context(project, tasks, risks, evm)

        # 6. Call LLM
        insight_text = await self._call_llm_api(context_str)

        # 7. Persist to DB
        insight = AIInsight(
            project_id=project_id,
            insight_text=insight_text,
            triggered_by=triggered_by,
        )
        self.db.add(insight)
        await self.db.commit()

        logger.info(
            "ai_project_audit_completed",
            project_id=str(project_id),
            provider=self.settings.LLM_PROVIDER,
        )
        return insight_text

    async def _calculate_evm(self, project: Project, tasks: List[Task]) -> Dict[str, Any]:
        """Compute current EVM metrics as of today."""
        status_date = date.today()
        bac = float(project.budget_total or 0)
        pv = 0.0
        ev = 0.0
        ac = 0.0

        for task in tasks:
            task_budget = (float(task.weight_percent or 0) / 100.0) * bac

            # PV
            if task.end_date_scheduled and task.end_date_scheduled <= status_date:
                pv += task_budget

            # Latest progress log
            log_result = await self.db.execute(
                select(ProgressLog)
                .where(ProgressLog.task_id == task.id)
                .where(ProgressLog.log_date <= status_date)
                .order_by(ProgressLog.log_date.desc())
                .limit(1)
            )
            log = log_result.scalar_one_or_none()
            if log:
                ev += (float(log.physical_percent or 0) / 100.0) * task_budget
                ac += float(log.actual_cost_dh or 0)

        metrics = EVMCalculator.calculate(pv=pv, ev=ev, ac=ac, bac=bac)
        return {
            "pv": round(pv, 2),
            "ev": round(ev, 2),
            "ac": round(ac, 2),
            "bac": round(bac, 2),
            "sv": metrics.sv,
            "cv": metrics.cv,
            "spi": metrics.spi,
            "cpi": metrics.cpi,
            "eac": metrics.eac,
            "vac": metrics.vac,
            "tcpi": metrics.tcpi,
            "status": metrics.status,
        }

    def _format_project_context(
        self,
        project: Project,
        tasks: List[Task],
        risks: List[Risk],
        evm: Dict[str, Any]
    ) -> str:
        """Format the project data into a structured context block for the LLM."""
        critical_path_tasks = [t.name for t in tasks if t.is_critical]
        delayed_tasks = [
            t.name for t in tasks
            if t.end_date_scheduled and t.end_date_scheduled < date.today() and t.status != "completed"
        ]

        task_list_str = "\n".join([
            f"- [{t.wbs_code}] {t.name}: Start={t.start_date_scheduled}, End={t.end_date_scheduled}, Duration={t.duration_days}d, Float={t.total_float}d, Critical={t.is_critical}, Status={t.status}"
            for t in tasks
        ])

        risk_list_str = "\n".join([
            f"- {r.title} ({r.category}): Score={r.risk_score} (Prob={r.probability}, Imp={r.impact}), Status={r.status}, Mitigation={r.mitigation}"
            for r in risks
        ])

        cpi_val = evm['cpi']
        cpi_label = "N/A (no cost recorded)" if cpi_val is None else (
            "Under/On budget" if cpi_val >= 1.0 else "Over budget"
        )
        cpi_display = "N/A" if cpi_val is None else str(cpi_val)
        tcpi_display = "N/A" if evm.get('tcpi') is None else str(evm['tcpi'])

        context = f"""
PROJECT METADATA:
- Name: {project.name}
- Status: {project.status}
- Dates: {project.start_date} to {project.end_date}
- Budget (BAC): {evm['bac']:,} DH

EARNED VALUE PERFORMANCE METRICS:
- Planned Value (PV): {evm['pv']:,} DH
- Earned Value (EV): {evm['ev']:,} DH
- Actual Cost (AC): {evm['ac']:,} DH
- Schedule Variance (SV): {evm.get('sv', 0):,} DH
- Cost Variance (CV): {evm.get('cv', 0):,} DH
- Schedule Performance Index (SPI): {evm['spi']} ({"Ahead/On track" if evm['spi'] >= 1.0 else "Behind schedule"})
- Cost Performance Index (CPI): {cpi_display} ({cpi_label})
- Estimate at Completion (EAC): {evm['eac']:,} DH
- Variance at Completion (VAC): {evm['vac']:,} DH
- To-Complete Performance Index (TCPI): {tcpi_display}
- Project EVM Status: {evm['status'].upper()}

SCHEDULE ANALYSIS:
- Total Tasks: {len(tasks)}
- Critical Path Tasks: {critical_path_tasks}
- Delayed Tasks: {delayed_tasks}

ACTIVE PROJECT RISKS:
{risk_list_str if risks else "No risks identified."}

TASK WORK BREAKDOWN:
{task_list_str if tasks else "No tasks scheduled."}
"""
        return context

    async def _call_llm_api(self, context_str: str) -> str:
        """Invoke external LLM provider API (Ollama/OpenAI/Anthropic) with fallback support."""
        system_prompt = (
            "You are an expert Project Control Analyst and Risk Engineer. "
            "Analyze the project performance data provided and return a comprehensive, "
            "professional Project Risk and Performance Audit in Markdown format. "
            "Be direct, clear, and actionable. Do not output anything other than the Markdown report. "
            "Address project delay risks, critical path concerns, resource constraints, "
            "and cost/schedule variance (CPI, SPI) trends."
        )

        provider = self.settings.LLM_PROVIDER.lower()
        base_url = self.settings.LLM_BASE_URL
        api_key = self.settings.LLM_API_KEY
        model = self.settings.LLM_MODEL

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if provider in ("openai", "ollama"):
                    # Both use OpenAI completion format
                    url = f"{base_url.rstrip('/')}/chat/completions"
                    headers = {
                        "Content-Type": "application/json",
                    }
                    if api_key:
                        headers["Authorization"] = f"Bearer {api_key}"

                    payload = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": context_str},
                        ],
                        "temperature": 0.3,
                    }

                    response = await client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    return str(data["choices"][0]["message"]["content"])

                elif provider == "anthropic":
                    url = f"{base_url.rstrip('/')}/v1/messages"
                    headers = {
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    }
                    payload = {
                        "model": model,
                        "max_tokens": 4000,
                        "system": system_prompt,
                        "messages": [
                            {"role": "user", "content": context_str}
                        ],
                        "temperature": 0.3,
                    }

                    response = await client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    return str(data["content"][0]["text"])

                else:
                    raise ValueError(f"Unknown LLM provider: {provider}")

        except Exception as e:
            logger.warning("llm_api_call_failed_using_fallback", error=str(e))
            return self._generate_fallback_audit(context_str)

    def _generate_fallback_audit(self, context_str: str) -> str:
        """Compile a highly structured, accurate fallback report if LLM API is unavailable."""
        # Parse context info for custom fallback report
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Simple analysis indicators
        cpi = 1.0
        spi = 1.0
        for line in context_str.split("\n"):
            if "Cost Performance Index (CPI):" in line:
                try:
                    cpi = float(line.split(":")[-1].split("(")[0].strip())
                except ValueError:
                    pass
            elif "Schedule Performance Index (SPI):" in line:
                try:
                    spi = float(line.split(":")[-1].split("(")[0].strip())
                except ValueError:
                    pass

        budget_status = "ON BUDGET" if cpi == 1.0 else ("UNDER BUDGET" if cpi > 1.0 else "OVER BUDGET")
        schedule_status = "ON SCHEDULE" if spi == 1.0 else ("AHEAD OF SCHEDULE" if spi > 1.0 else "BEHIND SCHEDULE")

        report = f"""# NEXUS AI Project Performance & Risk Audit

> [!NOTE]
> **AI Audit Offline Fallback Mode**
> This report was compiled by the local NEXUS rules engine on `{now_str}` as the LLM provider API was offline/unreachable.

## 1. Executive Performance Summary

Based on the latest project control metrics:
- **Cost Efficiency**: The project is currently **{budget_status}** with a Cost Performance Index (CPI) of **{cpi:.2f}**.
- **Schedule Efficiency**: The project is **{schedule_status}** with a Schedule Performance Index (SPI) of **{spi:.2f}**.

### Earned Value Table
| Metric | Status / Value |
| :--- | :--- |
| CPI (Cost Index) | `{cpi:.3f}` |
| SPI (Schedule Index) | `{spi:.3f}` |
| EVM Health | `{"HEALTHY" if (cpi >= 0.9 and spi >= 0.9) else "AT RISK" if (cpi >= 0.8 and spi >= 0.8) else "CRITICAL"}` |

---

## 2. Schedule & Critical Path Risk Analysis

### Critical Path Observations
The Critical Path comprises the sequence of dependent tasks that determine the minimum project duration. Delays in these tasks will directly translate to a project end-date slippage.
- Review all active tasks on the critical path immediately to ensure sufficient resource allocations.
- Focus on buffer management; any tasks with `Float = 0` must have strict daily tracking.

### Delayed Task Warnings
- Ensure progress logs are up-to-date. Late reporting can artificially degrade the Schedule Performance Index (SPI).
- If tasks are legitimately delayed, consider resource leveling or fast-tracking successors if they are not on the critical path.

---

## 3. Risk Log & Contingency Analysis

- **Risk Scoring**: Focus response plans on active risks with a risk score greater than 15.
- **Contingency Planning**: Ensure contingency factors are integrated into successor task durations for any active risks flagged with high probability/impact scores.
- **Resource Constraints**: High-priority tasks must be prioritized during daily standups to minimize bottlenecks.

## 4. Key Recommendations

1. **Verify WBS Weights**: Ensure task weight percentages align with the budget distribution to keep Earned Value (EV) computations accurate.
2. **Execute Resource Leveling**: If resource over-allocations exist, run the serial-associative leveling tool to adjust task start dates without overloading staff.
3. **Commit Regular Baselines**: Lock the current schedule as a baseline (e.g. `B0`) before performing any resource leveling to preserve variance measurement capabilities.
"""
        return report
