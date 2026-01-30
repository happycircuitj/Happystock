"""Scoring engine for candidate signals."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

import numpy as np


@dataclass
class ScoreEngine:
    weights: Dict[str, float] = field(
        default_factory=lambda: {
            "signal_type": 28,
            "cmf": 16,
            "cmf_delta": 10,
            "macd": 12,
            "vwap": 6,
            "vol_bonus": 5,
            "ma_state": 5,
            "recency": 4,
            "atr_penalty": -4,
            "candle_bonus": 2,
            "obv": 4,
            "prox": 8,
        }
    )

    def calculate_score(self, context: dict, signal_type: str) -> float:
        components = self._calculate_components(context, signal_type)
        total_score = sum(self.weights.get(key, 0) * value for key, value in components.items())
        return round(float(total_score), 2)

    def _calculate_components(self, context: dict, signal_type: str) -> Dict[str, float]:
        signal_weight = {"BOTH": 1.0, "OBV": 0.85, "ADL": 0.8}.get(signal_type, 0.0)
        cmf = context.get("cmf", 0.0)
        cmf_delta = context.get("cmf_delta", 0.0)
        macd_hist = context.get("macd_hist", 0.0)
        atr_pct = context.get("atr_pct", 0.0)
        vwap_in_band = 1.0 if context.get("vwap_in_band", False) else 0.0
        vol_bonus = 1.0 if context.get("vol_above_ma20", False) else 0.0
        ma_state = 1.0 if context.get("close_above_sma20", False) else 0.0
        recency = max(0.0, 1.0 - context.get("days_since_signal", 0) / 10)
        candle_bonus = 1.0 if context.get("bullish_candle", False) else 0.0
        obv_trend = context.get("obv_trend", 0.0)
        prox = context.get("prox_to_struct_high", 0.0)

        return {
            "signal_type": signal_weight,
            "cmf": (cmf + 1) / 2,
            "cmf_delta": np.tanh(cmf_delta / 0.12),
            "macd": np.tanh(macd_hist / max(atr_pct, 1e-6) / 0.12),
            "vwap": vwap_in_band,
            "vol_bonus": vol_bonus,
            "ma_state": ma_state,
            "recency": recency,
            "atr_penalty": -atr_pct,
            "candle_bonus": candle_bonus,
            "obv": obv_trend,
            "prox": prox,
        }
