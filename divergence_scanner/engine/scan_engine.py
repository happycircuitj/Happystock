"""Main scan engine."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd

from divergence_scanner.core.data_collector import DataCollector
from divergence_scanner.core.divergence_detector import detect_confirmed_divergence, detect_early_divergence, classify_signal
from divergence_scanner.core.indicators import add_indicators
from divergence_scanner.core.universe_manager import UniverseManager
from divergence_scanner.engine.parallel_processor import ParallelProcessor
from divergence_scanner.filters.pipeline import FilterPipeline
from divergence_scanner.scoring.score_engine import ScoreEngine
from divergence_scanner.scoring.trade_planner import TradePlanner
from divergence_scanner.utils.logger import get_logger
from divergence_scanner.utils.validators import ConfigValidator


@dataclass
class ScanEngine:
    def __post_init__(self) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.validator = ConfigValidator()
        self.universe_manager = UniverseManager()
        self.collector = DataCollector()
        self.score_engine = ScoreEngine()
        self.trade_planner = TradePlanner()

    def scan_with_config(self, config: Dict) -> pd.DataFrame:
        validated_config = self.validator.validate_config(config)
        pipeline = FilterPipeline(validated_config)
        universe = self.universe_manager.load_universe(validated_config)
        if universe.empty:
            return pd.DataFrame()
        symbols = (
            validated_config["SAMPLE_SYMBOLS"] if validated_config.get("TEST_SAMPLE") else universe["Symbol"].tolist()
        )
        if validated_config.get("PARALLEL", True):
            processor = ParallelProcessor(validated_config.get("MAX_WORKERS", 8))
            results = processor.run(lambda sym: self._scan_symbol(sym, validated_config, pipeline), symbols)
        else:
            results = [self._scan_symbol(sym, validated_config, pipeline) for sym in symbols]
        rows = [row for row in results if row]
        return pd.DataFrame(rows)

    def _scan_symbol(self, symbol: str, config: Dict, pipeline: FilterPipeline) -> Dict:
        df = self.collector.fetch_ohlcv(symbol, config.get("START", "2000-01-01"), config.get("END", "2099-12-31"))
        if df.empty:
            return {}
        df = add_indicators(df)
        divergence = detect_confirmed_divergence(df, {"PIVOT_K": config["PIVOT_K"], "LOOKBACK": config["LOOKBACK"]})
        stage = "CONFIRMED"
        if not divergence:
            divergence = detect_early_divergence(df, {"PIVOT_K": config["PIVOT_K"], "LOOKBACK": config["LOOKBACK"]})
            stage = "EARLY"
        if not divergence:
            return {}
        signal_type = classify_signal(divergence)
        context = self._build_context(df, divergence)
        passed, reasons = pipeline.apply_filters({"symbol": symbol}, context)
        score = self.score_engine.calculate_score(context, signal_type)
        trade_plan = self.trade_planner.create_trade_plan(context, {"SL_ATR": 1.5, "TP_ATR": 3.0})
        return {
            "symbol": symbol,
            "signal_type": signal_type,
            "stage": stage,
            "p1": divergence["p1"],
            "p2": divergence["p2"],
            "struct_high": divergence["struct_high"],
            "score": score,
            "passed": passed,
            "reject_reasons": reasons,
            "trade_plan": trade_plan,
        }

    def _build_context(self, df: pd.DataFrame, divergence: Dict) -> Dict:
        p2 = divergence["p2"]
        close = float(df.loc[p2, "Close"])
        atr = float(df.loc[p2, "ATR"])
        cmf = float(df.loc[p2, "CMF"])
        macd_hist = float(df.loc[p2, "MACD_HIST"])
        volume = float(df.loc[p2, "Volume"])
        volume_ma20 = float(df["Volume"].rolling(20).mean().iloc[-1])
        turnover = volume * close
        turnover_ma20 = float((df["Volume"] * df["Close"]).rolling(20).mean().iloc[-1])
        rsi = float(df.loc[p2, "RSI"])
        atr_pct = atr / close * 100 if close else 0.0
        return {
            "close": close,
            "atr": atr,
            "atr_pct": atr_pct,
            "cmf": cmf,
            "cmf_delta": float(df["CMF"].diff().iloc[-1]),
            "macd_hist": macd_hist,
            "volume": volume,
            "volume_ma20": volume_ma20,
            "vol_above_ma20": volume > volume_ma20,
            "turnover_p2": turnover,
            "turnover_ma20": turnover_ma20,
            "close_above_sma20": close > float(df["SMA20"].iloc[-1]),
            "rsi": rsi,
            "days_since_signal": 0,
            "vwap_in_band": True,
            "avwap": close,
            "bullish_candle": df["Close"].iloc[-1] > df["Open"].iloc[-1],
            "obv_trend": float(df["OBV"].diff().iloc[-5:].mean() > 0),
            "prox_to_struct_high": float(close / divergence.get("struct_high", close)) if divergence.get("struct_high") else 0.0,
        }
