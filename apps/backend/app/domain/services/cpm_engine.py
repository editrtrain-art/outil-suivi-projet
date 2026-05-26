"""Critical Path Method (CPM) Engine.

Pure algorithmic implementation of the CPM algorithm, independent of the database.
Supports FS, SS, FF, SF dependencies with lag/lead.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Dict, List, Set, Optional

from app.core.exceptions import ValidationError, CircularDependencyError


class DependencyType(str, Enum):
    FS = "FS"  # Finish-to-Start
    SS = "SS"  # Start-to-Start
    FF = "FF"  # Finish-to-Finish
    SF = "SF"  # Start-to-Finish


@dataclass(frozen=True)
class DependencyLink:
    predecessor_id: uuid.UUID
    dep_type: DependencyType = DependencyType.FS
    lag_days: int = 0


@dataclass
class TaskNode:
    id: uuid.UUID
    duration_days: int
    dependencies: List[DependencyLink] = field(default_factory=list)
    
    # CPM Results
    early_start: int = 0  # Days from project start
    early_finish: int = 0
    late_start: int = 0
    late_finish: int = 0
    total_float: int = 0
    free_float: int = 0
    is_critical: bool = False


class CPMEngine:
    """Core CPM Algorithm implementation."""

    def __init__(self, tasks: List[TaskNode]) -> None:
        self.nodes: Dict[uuid.UUID, TaskNode] = {t.id: t for t in tasks}
        self.successors: Dict[uuid.UUID, List[uuid.UUID]] = {t.id: [] for t in tasks}
        
        # Build adjacency list for successors
        for task in tasks:
            for dep in task.dependencies:
                if dep.predecessor_id in self.successors:
                    self.successors[dep.predecessor_id].append(task.id)
                else:
                    raise ValidationError(f"Predecessor {dep.predecessor_id} not found in task list")

    def compute(self) -> Dict[uuid.UUID, TaskNode]:
        """Run the full CPM calculation."""
        if not self.nodes:
            return {}

        sorted_ids = self._topological_sort()
        self._forward_pass(sorted_ids)
        self._backward_pass(sorted_ids)
        self._identify_critical_path()
        
        return self.nodes

    def _topological_sort(self) -> List[uuid.UUID]:
        """Kahn's algorithm for topological sorting and cycle detection."""
        in_degree = {node_id: 0 for node_id in self.nodes}
        for node_id in self.nodes:
            for dep in self.nodes[node_id].dependencies:
                in_degree[node_id] += 1

        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        sorted_list = []

        while queue:
            u = queue.pop(0)
            sorted_list.append(u)
            
            for v in self.successors[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        if len(sorted_list) != len(self.nodes):
            # Find a node involved in the cycle for the error message
            remaining = set(self.nodes.keys()) - set(sorted_list)
            raise CircularDependencyError(cycle=[str(node_id) for node_id in list(remaining)[:3]])

        return sorted_list

    def _forward_pass(self, sorted_ids: List[uuid.UUID]) -> None:
        """Calculate Early Start (ES) and Early Finish (EF)."""
        for node_id in sorted_ids:
            node = self.nodes[node_id]
            
            if not node.dependencies:
                node.early_start = 0
            else:
                es = 0
                for dep in node.dependencies:
                    pred = self.nodes[dep.predecessor_id]
                    
                    if dep.dep_type == DependencyType.FS:
                        val = pred.early_finish + dep.lag_days
                    elif dep.dep_type == DependencyType.SS:
                        val = pred.early_start + dep.lag_days
                    elif dep.dep_type == DependencyType.FF:
                        val = pred.early_finish + dep.lag_days - node.duration_days
                    elif dep.dep_type == DependencyType.SF:
                        val = pred.early_start + dep.lag_days - node.duration_days
                    else:
                        val = pred.early_finish + dep.lag_days
                        
                    es = max(es, val)
                
                node.early_start = es
            
            node.early_finish = node.early_start + node.duration_days

    def _backward_pass(self, sorted_ids: List[uuid.UUID]) -> None:
        """Calculate Late Start (LS) and Late Finish (LF)."""
        # Find the project finish time (max EF of all nodes)
        project_finish = max(node.early_finish for node in self.nodes.values())
        
        # Process in reverse topological order
        for node_id in reversed(sorted_ids):
            node = self.nodes[node_id]
            
            successors_ids = self.successors[node_id]
            if not successors_ids:
                node.late_finish = project_finish
            else:
                lf = project_finish
                for succ_id in successors_ids:
                    succ = self.nodes[succ_id]
                    # Find the dependency link from succ to node
                    for dep in succ.dependencies:
                        if dep.predecessor_id == node_id:
                            if dep.dep_type == DependencyType.FS:
                                val = succ.late_start - dep.lag_days
                            elif dep.dep_type == DependencyType.SS:
                                val = succ.late_start - dep.lag_days + node.duration_days
                            elif dep.dep_type == DependencyType.FF:
                                val = succ.late_finish - dep.lag_days
                            elif dep.dep_type == DependencyType.SF:
                                val = succ.late_finish - dep.lag_days + node.duration_days
                            else:
                                # Default: treat as FS for unknown types
                                val = succ.late_start - dep.lag_days
                            lf = min(lf, val)
                
                node.late_finish = lf
            
            node.late_start = node.late_finish - node.duration_days
            node.total_float = node.late_start - node.early_start
            node.free_float = (
                min(
                    (
                        self.nodes[succ_id].early_start
                        - node.early_finish
                        for succ_id in self.successors[node_id]
                    ),
                    default=node.total_float,
                )
            )

    def _identify_critical_path(self) -> None:
        """Flag tasks on the critical path (Total Float = 0)."""
        for node in self.nodes.values():
            node.is_critical = node.total_float <= 0
