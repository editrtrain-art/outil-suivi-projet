"""Unit tests for the CPMEngine.

Covers basic paths, parallel branches, different dependency types (FS, SS, FF, SF),
lag/lead, and cycle detection.
"""

from __future__ import annotations

import uuid
import pytest

from app.domain.services.cpm_engine import CPMEngine, TaskNode, DependencyLink, DependencyType
from app.core.exceptions import CircularDependencyError


def test_cpm_simple_linear_path():
    """Test A -> B -> C (all FS)."""
    id_a, id_b, id_c = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    
    tasks = [
        TaskNode(id=id_a, duration_days=5),
        TaskNode(id=id_b, duration_days=3, dependencies=[DependencyLink(id_a)]),
        TaskNode(id=id_c, duration_days=2, dependencies=[DependencyLink(id_b)]),
    ]
    
    engine = CPMEngine(tasks)
    result = engine.compute()
    
    # Task A
    assert result[id_a].early_start == 0
    assert result[id_a].early_finish == 5
    assert result[id_a].is_critical is True
    
    # Task B
    assert result[id_b].early_start == 5
    assert result[id_b].early_finish == 8
    assert result[id_b].is_critical is True
    
    # Task C
    assert result[id_c].early_start == 8
    assert result[id_c].early_finish == 10
    assert result[id_c].is_critical is True


def test_cpm_parallel_branches():
    """
    Test parallel branches:
    A (5) -> B (3) -> D (2)
    A (5) -> C (1) -> D (2)
    """
    id_a, id_b, id_c, id_d = uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    
    tasks = [
        TaskNode(id=id_a, duration_days=5),
        TaskNode(id=id_b, duration_days=3, dependencies=[DependencyLink(id_a)]),
        TaskNode(id=id_c, duration_days=1, dependencies=[DependencyLink(id_a)]),
        TaskNode(id=id_d, duration_days=2, dependencies=[DependencyLink(id_b), DependencyLink(id_c)]),
    ]
    
    engine = CPMEngine(tasks)
    result = engine.compute()
    
    # Path A-B-D is 5+3+2 = 10
    # Path A-C-D is 5+1+2 = 8
    
    assert result[id_d].early_finish == 10
    assert result[id_b].is_critical is True
    assert result[id_c].is_critical is False
    assert result[id_c].total_float == 2


def test_cpm_with_lag():
    """Test A -> B (FS) with lag of 2 days."""
    id_a, id_b = uuid.uuid4(), uuid.uuid4()
    
    tasks = [
        TaskNode(id=id_a, duration_days=5),
        TaskNode(id=id_b, duration_days=3, dependencies=[DependencyLink(id_a, lag_days=2)]),
    ]
    
    engine = CPMEngine(tasks)
    result = engine.compute()
    
    assert result[id_a].early_finish == 5
    assert result[id_b].early_start == 7
    assert result[id_b].early_finish == 10


def test_cpm_dependency_types():
    """Test different dependency types: SS and FF."""
    id_a, id_b, id_c = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    
    tasks = [
        TaskNode(id=id_a, duration_days=10),
        # B starts 2 days after A starts (SS)
        TaskNode(id=id_b, duration_days=5, dependencies=[DependencyLink(id_a, dep_type=DependencyType.SS, lag_days=2)]),
        # C finishes 2 days after A finishes (FF)
        TaskNode(id=id_c, duration_days=5, dependencies=[DependencyLink(id_a, dep_type=DependencyType.FF, lag_days=2)]),
    ]
    
    engine = CPMEngine(tasks)
    result = engine.compute()
    
    # Task A: ES=0, EF=10
    # Task B: ES = A.ES + 2 = 2. EF = 2 + 5 = 7
    assert result[id_b].early_start == 2
    assert result[id_b].early_finish == 7
    
    # Task C: EF = A.EF + 2 = 12. ES = 12 - 5 = 7
    assert result[id_c].early_finish == 12
    assert result[id_c].early_start == 7


def test_cpm_circular_dependency():
    """Test that a circular dependency raises CircularDependencyError."""
    id_a, id_b = uuid.uuid4(), uuid.uuid4()
    
    tasks = [
        TaskNode(id=id_a, duration_days=5, dependencies=[DependencyLink(id_b)]),
        TaskNode(id=id_b, duration_days=5, dependencies=[DependencyLink(id_a)]),
    ]
    
    engine = CPMEngine(tasks)
    with pytest.raises(CircularDependencyError):
        engine.compute()
