from __future__ import annotations

from dataclasses import dataclass, field

@dataclass
class BranchRule:
    student_a: int
    student_b: int
    mode: str   # "together" or "separate"

@dataclass
class BPNode:
    node_id: int
    depth: int
    branch_rules: list[BranchRule] = field(default_factory=list)
    routes: list = field(default_factory=list)

