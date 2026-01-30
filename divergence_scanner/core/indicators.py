"""Technical indicator calculations."""
from __future__ import annotations

from typing import Dict

import numpy as np
import pandas as pd


REQUIRED_INDICATORS: Dict[str, str] = {
    "OBV": "On-Balance Volume",
    "ADL": "Accumulation/Distribution Line",
    "CMF": "Chaikin Money Flow (n=20)",
    "RSI": "Relative Strength Index (n=14)",
    "MACD": "MACD (12,26,9)",
    "ATR": "Average True Range (n=14)",
    "SMA": "Simple Moving Average",
    "AVWAP": "Anchored VWAP",
}


def calc_obv(df: pd.DataFrame) -> pd.Series:
    direction = np.sign(df["Close"].diff()).fillna(0)
    return (direction * df["Volume"]).cumsum()


def calc_adl(df: pd.DataFrame) -> pd.Series:
    mfm = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / (df["High"] - df["Low"]).replace(0, np.nan)
    mfv = mfm.fillna(0) * df["Volume"]
    return mfv.cumsum()


def calc_cmf(df: pd.DataFrame, window: int = 20) -> pd.Series:
    mfm = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / (df["High"] - df["Low"]).replace(0, np.nan)
    mfv = mfm.fillna(0) * df["Volume"]
    return mfv.rolling(window).sum() / df["Volume"].rolling(window).sum().replace(0, np.nan)


def calc_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def calc_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return pd.DataFrame({"MACD": macd_line, "MACD_SIGNAL": signal_line, "MACD_HIST": hist})


def calc_atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window).mean()


def calc_sma(series: pd.Series, window: int = 20) -> pd.Series:
    return series.rolling(window).mean()


def calc_anchored_vwap(df: pd.DataFrame, anchor_date: pd.Timestamp) -> float:
    anchor_idx = df.index.get_indexer([anchor_date], method="nearest")[0]
    if anchor_idx == -1:
        return np.nan
    slice_data = df.iloc[anchor_idx:]
    typical_price = (slice_data["High"] + slice_data["Low"] + slice_data["Close"]) / 3
    volume_sum = slice_data["Volume"].sum()
    if volume_sum <= 0:
        return np.nan
    return float((typical_price * slice_data["Volume"]).sum() / volume_sum)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add required indicators to dataframe.

    Args:
        df: OHLCV dataframe.

    Returns:
        Dataframe with indicator columns.
    """
    df = df.copy()
    df["OBV"] = calc_obv(df)
    df["ADL"] = calc_adl(df)
    df["CMF"] = calc_cmf(df)
    df["RSI"] = calc_rsi(df["Close"])
    macd = calc_macd(df["Close"])
    df = df.join(macd)
    df["ATR"] = calc_atr(df)
    df["SMA20"] = calc_sma(df["Close"], 20)
    return df
