"""Configuration presets and defaults."""
from __future__ import annotations

from typing import Dict, Any


PRESETS: Dict[str, Dict[str, Any]] = {
    "탐색형": {
        "WEIGHTED_FILTER": False,
        "RSI_MODE": "off",
        "MIN_TURNOVER": 3e8,
        "REGIME_MODE": "off",
    },
    "확정형": {
        "WEIGHTED_FILTER": True,
        "SCORE_THRESHOLD": 55.0,
        "RSI_MODE": "soft",
        "MIN_TURNOVER": 8e8,
    },
    "리스크온": {
        "MIN_TURNOVER": 1.2e9,
        "ATR_PCT_MAX": 12.0,
        "REGIME_MODE": "soft",
    },
    "리스크오프": {
        "MIN_TURNOVER": 2.5e9,
        "ATR_PCT_MAX": 8.0,
        "RSI_MODE": "strict",
        "SCORE_THRESHOLD": 60.0,
        "REGIME_MODE": "strict",
    },
}

DEFAULT_CONFIG: Dict[str, Any] = {
    "LOOKBACK": 60,
    "PIVOT_K": 2,
    "CACHE_DIR": "data",
    "PARALLEL": True,
    "MAX_WORKERS": 8,
    "TEST_SAMPLE": False,
    "SAMPLE_SYMBOLS": [],
    "MIN_TURNOVER": 8e8,
    "MIN_ABS_TURNOVER_ON_SIGNAL": 1e8,
    "ATR_PCT_MAX": 15.0,
    "REGIME_MODE": "off",
    "REGIME_FAST": 20,
    "REGIME_SLOW": 60,
    "REGIME_SLOPE_DAYS": 5,
    "RSI_MODE": "soft",
    "SCORE_THRESHOLD": 55.0,
}


def get_preset(name: str) -> Dict[str, Any]:
    """Return a preset configuration merged with defaults.

    Args:
        name: Preset name.

    Returns:
        Merged configuration dictionary.
    """
    preset = PRESETS.get(name, {})
    merged = DEFAULT_CONFIG.copy()
    merged.update(preset)
    return merged
