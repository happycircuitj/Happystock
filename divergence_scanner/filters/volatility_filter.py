"""Volatility filter implementation."""
from __future__ import annotations

from typing import Tuple

from divergence_scanner.filters.base_filter import BaseFilter


class VolatilityFilter(BaseFilter):
    def check(self, candidate: dict, context: dict) -> Tuple[bool, str]:
        atr_pct = context.get("atr_pct")
        if atr_pct is None:
            return False, "atr_pct_missing"
        if atr_pct > self.config.get("ATR_PCT_MAX", float("inf")):
            return False, "atr_pct"
        return True, ""
