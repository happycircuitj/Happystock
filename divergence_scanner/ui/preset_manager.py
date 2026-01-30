"""Preset manager for UI selections."""
from __future__ import annotations

from typing import Dict, Any

from divergence_scanner.utils.config import get_preset


class PresetManager:
    def get_preset(self, name: str) -> Dict[str, Any]:
        return get_preset(name)
