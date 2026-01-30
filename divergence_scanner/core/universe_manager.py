"""Universe management and caching."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

import pandas as pd

from divergence_scanner.utils.logger import get_logger


EXCLUDE_PATTERNS = [
    "ETF",
    "ETN",
    "KODEX",
    "TIGER",
    "KBSTAR",
    "HANARO",
    "ARIRANG",
    "KOSEF",
    "TREX",
    "SOL",
    "FOCUS",
    "KINDEX",
    "리츠",
    "REIT",
    "스팩",
    "SPAC",
    "인버스",
    "선물",
    "레버리지",
]


def is_preferred_stock(name: str) -> bool:
    """Check if a stock is preferred based on name suffix patterns."""
    return name.endswith(("우", "우B", "우C")) or ("우(" in name and ")" in name)


def safe_listing_filter(df: pd.DataFrame, days: int = 180) -> pd.DataFrame:
    """Filter out recently listed stocks with timezone safety.

    Args:
        df: Universe dataframe.
        days: Cutoff days.

    Returns:
        Filtered dataframe.
    """
    listing_dates = pd.to_datetime(df["ListingDate"], errors="coerce")
    if hasattr(listing_dates, "dt"):
        listing_dates = listing_dates.dt.tz_localize(None)
    cutoff = pd.Timestamp.now().replace(tzinfo=None) - pd.Timedelta(days=days)
    return df[listing_dates.isna() | (listing_dates < cutoff)]


@dataclass
class UniverseManager:
    cache_dir: str = "data"

    def __post_init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        os.makedirs(self.cache_dir, exist_ok=True)

    def _cache_path(self) -> str:
        return os.path.join(self.cache_dir, "universe_cache.csv")

    def load_universe(self, config: dict) -> pd.DataFrame:
        """Load the universe with caching and fallbacks.

        Args:
            config: Configuration dictionary.

        Returns:
            Universe dataframe.
        """
        cache_path = self._cache_path()
        if os.path.exists(cache_path):
            self.logger.info("Loading universe from cache")
            return pd.read_csv(cache_path)

        universe = self._fetch_universe()
        if universe.empty:
            self.logger.warning("Universe fetch failed")
            return universe

        filtered = self._filter_universe(universe)
        filtered.to_csv(cache_path, index=False)
        return filtered

    def _fetch_universe(self) -> pd.DataFrame:
        """Fetch universe from providers."""
        try:
            import FinanceDataReader as fdr

            df = fdr.StockListing("KRX")
            df.rename(
                columns={
                    "Code": "Symbol",
                    "Name": "Name",
                    "Market": "Market",
                    "ListingDate": "ListingDate",
                },
                inplace=True,
            )
            return df[["Symbol", "Name", "Market", "ListingDate"]]
        except Exception as exc:  # pragma: no cover - network dependent
            self.logger.warning("FinanceDataReader failed: %s", exc)

        try:
            from pykrx import stock

            symbols = stock.get_market_ticker_list()
            names = [stock.get_market_ticker_name(sym) for sym in symbols]
            return pd.DataFrame({"Symbol": symbols, "Name": names, "Market": "KRX"})
        except Exception as exc:  # pragma: no cover - network dependent
            self.logger.error("PyKRX failed: %s", exc)
        return pd.DataFrame()

    def _filter_universe(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df = df[~df["Name"].str.contains("|".join(EXCLUDE_PATTERNS), na=False)]
        df = df[~df["Name"].apply(is_preferred_stock)]
        df = safe_listing_filter(df)
        return df.reset_index(drop=True)
