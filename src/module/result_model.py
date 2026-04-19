
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RMPResult:
    success: bool
    pi: dict
    mu: float
    obj_value: float
    routes: list
    lambda_values: list[float]
    is_integer: bool

