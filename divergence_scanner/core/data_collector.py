"""Data collection utilities for OHLCV and indices."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Optional

import pandas as pd

from divergence_scanner.utils.logger import get_logger
from divergence_scanner.utils.validators import DataValidator


@dataclass
class DataCollector:
    cache_dir: str = "data"
    max_retries: int = 3
    retry_delay: float = 0.5

    def __post_init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        os.makedirs(self.cache_dir, exist_ok=True)
        self.validator = DataValidator()

    def fetch_ohlcv(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """Fetch OHLCV data with retry and fallback.

        Args:
            symbol: Stock ticker.
            start: Start date string.
            end: End date string.

        Returns:
            OHLCV dataframe.
        """
        cache_path = os.path.join(self.cache_dir, f"ohlcv_{symbol}.csv")
        if os.path.exists(cache_path):
            df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
            if self.validator.validate_ohlcv(df).valid:
                return df

        df = pd.DataFrame()
        for attempt in range(self.max_retries):
            df = self._fetch_from_fdr(symbol, start, end)
            if df.empty:
                df = self._fetch_from_pykrx(symbol, start, end)
            if not df.empty:
                break
            time.sleep(self.retry_delay)
            self.logger.warning("Retrying fetch for %s (%s/%s)", symbol, attempt + 1, self.max_retries)

        if not df.empty and self.validator.validate_ohlcv(df).valid:
            df.to_csv(cache_path)
            return df
        return pd.DataFrame()

    def _fetch_from_fdr(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        try:
            import FinanceDataReader as fdr

            df = fdr.DataReader(symbol, start, end)
            return df
        except Exception as exc:  # pragma: no cover - external dependency
            self.logger.warning("FinanceDataReader fetch failed: %s", exc)
        return pd.DataFrame()

    def _fetch_from_pykrx(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        try:
            from pykrx import stock

            df = stock.get_market_ohlcv_by_date(start, end, symbol)
            df.rename(
                columns={
                    "시가": "Open",
                    "고가": "High",
                    "저가": "Low",
                    "종가": "Close",
                    "거래량": "Volume",
                },
                inplace=True,
            )
            return df
        except Exception as exc:  # pragma: no cover - external dependency
            self.logger.warning("PyKRX fetch failed: %s", exc)
        return pd.DataFrame()

    def fetch_market_index(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """Fetch market index data for regime filter.

        Args:
            symbol: Index symbol.
            start: Start date.
            end: End date.

        Returns:
            Index dataframe with Volume column.
        """
        df = self.fetch_ohlcv(symbol, start, end)
        if df.empty:
            return df
        if "Volume" not in df.columns:
            df["Volume"] = 0
        return df
