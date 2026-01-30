"""Validation helpers for configuration and data."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Tuple

import pandas as pd


@dataclass
class ValidationResult:
    valid: bool
    message: str = ""


class ConfigValidator:
    """Validate scanner configuration values."""

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration and return sanitized config.

        Args:
            config: Configuration dictionary.

        Returns:
            Sanitized configuration dictionary.
        """
        sanitized = dict(config)
        lookback = int(sanitized.get("LOOKBACK", 60))
        if lookback <= 0:
            raise ValueError("LOOKBACK must be positive")
        sanitized["LOOKBACK"] = lookback
        pivot_k = int(sanitized.get("PIVOT_K", 2))
        if pivot_k < 1:
            raise ValueError("PIVOT_K must be >= 1")
        sanitized["PIVOT_K"] = pivot_k
        return sanitized


class DataValidator:
    """Validate OHLCV dataframes."""

    def validate_ohlcv(self, df: pd.DataFrame) -> ValidationResult:
        """Check basic OHLCV consistency rules.

        Args:
            df: OHLCV dataframe.

        Returns:
            ValidationResult instance.
        """
        required = {"Open", "High", "Low", "Close", "Volume"}
        if not required.issubset(df.columns):
            return ValidationResult(False, "missing_columns")
        if (df["High"] < df["Low"]).any():
            return ValidationResult(False, "high_low_inconsistent")
        if (df[["Open", "High", "Low", "Close"]] <= 0).any().any():
            return ValidationResult(False, "price_non_positive")
        if (df["Volume"] < 0).any():
            return ValidationResult(False, "volume_negative")
        return ValidationResult(True, "ok")
