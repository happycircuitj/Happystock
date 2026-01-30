"""Market regime filter."""
from __future__ import annotations

from typing import Tuple

import pandas as pd

from divergence_scanner.filters.base_filter import BaseFilter


class RegimeFilter(BaseFilter):
    def check_market_regime(self, index_data: pd.DataFrame) -> bool:
        if self.config.get("REGIME_MODE", "off") == "off":
            return True
        close = index_data["Close"]
        ma_fast = close.rolling(self.config.get("REGIME_FAST", 20)).mean()
        ma_slow = close.rolling(self.config.get("REGIME_SLOW", 60)).mean()
        uptrend = close.iloc[-1] > ma_fast.iloc[-1] and ma_fast.iloc[-1] > ma_slow.iloc[-1]
        slope_days = self.config.get("REGIME_SLOPE_DAYS", 5)
        if len(ma_fast) <= slope_days:
            momentum = False
        else:
            momentum = ma_fast.iloc[-1] > ma_fast.iloc[-1 - slope_days]
        if self.config.get("REGIME_MODE", "off") == "strict":
            return uptrend and momentum
        return uptrend or momentum

    def check(self, candidate: dict, context: dict) -> Tuple[bool, str]:
        index_data = context.get("index_data")
        if index_data is None or not isinstance(index_data, pd.DataFrame):
            return False, "index_missing"
        return self.check_market_regime(index_data), "regime"
