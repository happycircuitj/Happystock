"""Base filter classes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any


@dataclass
class BaseFilter:
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    def is_enabled(self) -> bool:
        return self.enabled

    def check(self, candidate: dict, context: dict) -> Tuple[bool, str]:
        raise NotImplementedError
