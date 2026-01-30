"""Liquidity filter implementation."""
from __future__ import annotations

from typing import Tuple

from divergence_scanner.filters.base_filter import BaseFilter


class LiquidityFilter(BaseFilter):
    def check(self, candidate: dict, context: dict) -> Tuple[bool, str]:
        ma20_turnover = context.get("turnover_ma20")
        p2_turnover = context.get("turnover_p2")
        if ma20_turnover is None or p2_turnover is None:
            return False, "turnover_missing"
        if ma20_turnover < self.config.get("MIN_TURNOVER", 0):
            return False, "liquidity"
        if p2_turnover < self.config.get("MIN_ABS_TURNOVER_ON_SIGNAL", 0):
            return False, "abs_turnover"
        return True, ""
