"""Filter pipeline orchestration."""
from __future__ import annotations

from typing import List, Tuple

from divergence_scanner.filters.liquidity_filter import LiquidityFilter
from divergence_scanner.filters.regime_filter import RegimeFilter
from divergence_scanner.filters.technical_filter import RSIFilter, VWAPFilter, RecencyFilter, VolumeFilter
from divergence_scanner.filters.volatility_filter import VolatilityFilter


class FilterPipeline:
    """Multi-layer filter pipeline."""

    def __init__(self, config: dict) -> None:
        self.filters = [
            RegimeFilter(config),
            LiquidityFilter(config),
            VolatilityFilter(config),
            RSIFilter(config),
            VWAPFilter(config),
            RecencyFilter(config),
            VolumeFilter(config),
        ]

    def apply_filters(self, candidate: dict, context: dict) -> Tuple[bool, List[str]]:
        failed_reasons = []
        for filter_obj in self.filters:
            if not filter_obj.is_enabled():
                continue
            passed, reason = filter_obj.check(candidate, context)
            if not passed:
                failed_reasons.append(reason)
        return len(failed_reasons) == 0, failed_reasons
