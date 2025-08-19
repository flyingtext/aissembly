from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class Trace:
    on_enter: Callable[[str, Any], None] | None = None
    on_exit: Callable[[str, Any], None] | None = None
    on_branch: Callable[[str, Any], None] | None = None
