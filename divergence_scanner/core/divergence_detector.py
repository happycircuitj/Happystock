"""Divergence detection logic."""
from __future__ import annotations

from typing import Dict, List

import pandas as pd


def find_pivot_lows(series: pd.Series, k: int = 2, lookback: int = 60) -> List[pd.Timestamp]:
    """Identify pivot lows within lookback window."""
    if len(series) < (k * 2 + 3):
        return []
    tail_series = series.iloc[-lookback:] if lookback > 0 else series
    pivots: List[pd.Timestamp] = []
    for i in range(k, len(tail_series) - k):
        window = tail_series.iloc[i - k : i + k + 1]
        if tail_series.iloc[i] <= window.min():
            pivots.append(tail_series.index[i])
    return pivots


def calculate_structural_high(df: pd.DataFrame, p1: pd.Timestamp, p2: pd.Timestamp) -> float:
    """Calculate structural high between two pivot points."""
    segment = df.loc[p1:p2]
    return float(segment["High"].max()) if not segment.empty else float("nan")


def check_indicator_divergence(df: pd.DataFrame, indicator: str, p1: pd.Timestamp, p2: pd.Timestamp, params: Dict) -> bool:
    """Check if indicator shows higher low between pivots."""
    if indicator not in df.columns:
        return False
    i1 = df.loc[p1, indicator]
    i2 = df.loc[p2, indicator]
    return i2 > i1


def detect_confirmed_divergence(df: pd.DataFrame, params: Dict) -> Dict:
    """Detect confirmed divergence using two pivot lows."""
    price_pivots = find_pivot_lows(df["Low"], params["PIVOT_K"], params["LOOKBACK"])
    if len(price_pivots) < 2:
        return {}
    p1, p2 = price_pivots[-2], price_pivots[-1]
    if df.loc[p2, "Low"] >= df.loc[p1, "Low"]:
        return {}
    obv_divergence = check_indicator_divergence(df, "OBV", p1, p2, params)
    adl_divergence = check_indicator_divergence(df, "ADL", p1, p2, params)
    return {
        "obv_div": obv_divergence,
        "adl_div": adl_divergence,
        "p1": p1,
        "p2": p2,
        "struct_high": calculate_structural_high(df, p1, p2),
    }


def detect_early_divergence(df: pd.DataFrame, params: Dict) -> Dict:
    """Detect early divergence allowing lower lows."""
    price_pivots = find_pivot_lows(df["Low"], params["PIVOT_K"], params["LOOKBACK"])
    if not price_pivots:
        return {}
    p1 = price_pivots[-1]
    p2 = df.index[-1]
    if p2 <= p1:
        return {}
    if df.loc[p2, "Low"] > df.loc[p1, "Low"]:
        return {}
    pre_p1_segment = df.loc[df.index <= p1].iloc[-params["LOOKBACK"] :]
    p1_to_p2_segment = df.loc[(df.index > p1) & (df.index <= p2)]
    obv_div = p1_to_p2_segment["OBV"].min() > pre_p1_segment["OBV"].min()
    adl_div = p1_to_p2_segment["ADL"].min() > pre_p1_segment["ADL"].min()
    return {
        "obv_div": bool(obv_div),
        "adl_div": bool(adl_div),
        "p1": p1,
        "p2": p2,
        "struct_high": calculate_structural_high(df, p1, p2),
    }


def classify_signal(divergence_result: Dict) -> str:
    """Classify signal type based on divergence result."""
    obv_div = divergence_result.get("obv_div", False)
    adl_div = divergence_result.get("adl_div", False)
    if obv_div and adl_div:
        return "BOTH"
    if obv_div:
        return "OBV"
    if adl_div:
        return "ADL"
    return "NONE"
