"""Trade planning utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class TradePlanner:
    def create_trade_plan(self, context: dict, risk_params: Dict[str, float]) -> Dict[str, float]:
        """Create ATR-based trade plan."""
        entry = context["close"]
        atr = context["atr"]
        return {
            "Entry": entry,
            "StopLoss": entry - (risk_params["SL_ATR"] * atr),
            "TakeProfit": entry + (risk_params["TP_ATR"] * atr),
            "OneR": risk_params["SL_ATR"] * atr,
            "RiskReward": risk_params["TP_ATR"] / risk_params["SL_ATR"],
        }
