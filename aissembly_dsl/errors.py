from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Error(Exception):
    kind: str
    msg: str = ""
    data: Dict[str, Any] | None = None

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.kind}: {self.msg}"
