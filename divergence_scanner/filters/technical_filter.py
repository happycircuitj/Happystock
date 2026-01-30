"""Technical indicator filters."""
from __future__ import annotations

from typing import Tuple

from divergence_scanner.filters.base_filter import BaseFilter


class RSIFilter(BaseFilter):
    def check(self, candidate: dict, context: dict) -> Tuple[bool, str]:
        mode = self.config.get("RSI_MODE", "off")
        if mode == "off":
            return True, ""
        rsi = context.get("rsi")
        if rsi is None:
            return False, "rsi_missing"
        if mode == "strict":
            return rsi < 30, "rsi"
        return rsi < 40, "rsi"


class VWAPFilter(BaseFilter):
    def check(self, candidate: dict, context: dict) -> Tuple[bool, str]:
        close = context.get("close")
        avwap = context.get("avwap")
        if close is None or avwap is None:
            return False, "vwap_missing"
        band = self.config.get("VWAP_BAND", 0.05)
        lower = avwap * (1 - band)
        upper = avwap * (1 + band)
        if lower <= close <= upper:
            return True, ""
        return False, "vwap"


class RecencyFilter(BaseFilter):
    def check(self, candidate: dict, context: dict) -> Tuple[bool, str]:
        days_since = context.get("days_since_signal")
        if days_since is None:
            return False, "recency_missing"
        max_days = self.config.get("RECENCY_DAYS", 5)
        return days_since <= max_days, "recency"


class VolumeFilter(BaseFilter):
    def check(self, candidate: dict, context: dict) -> Tuple[bool, str]:
        volume = context.get("volume")
        ma20_volume = context.get("volume_ma20")
        if volume is None or ma20_volume is None:
            return False, "volume_missing"
        if volume > ma20_volume:
            return True, ""
        return False, "volume"
