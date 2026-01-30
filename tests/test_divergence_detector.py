import pandas as pd

from divergence_scanner.core.divergence_detector import detect_early_divergence
from divergence_scanner.core.universe_manager import safe_listing_filter


def test_early_signal_price_drop_allowed():
    dates = pd.date_range("2024-01-01", periods=6, freq="D")
    df = pd.DataFrame(
        {
            "Low": [10, 9, 8, 7, 6, 5],
            "High": [11, 10, 9, 8, 7, 6],
            "Close": [10.5, 9.5, 8.5, 7.5, 6.5, 5.5],
            "OBV": [100, 95, 90, 88, 87, 86],
            "ADL": [200, 195, 190, 188, 187, 186],
        },
        index=dates,
    )
    params = {"PIVOT_K": 1, "LOOKBACK": 6}
    result = detect_early_divergence(df, params)
    assert result


def test_timezone_safety():
    df = pd.DataFrame(
        {
            "Symbol": ["0001", "0002"],
            "Name": ["AAA", "BBB"],
            "Market": ["KOSPI", "KOSDAQ"],
            "ListingDate": ["2020-01-01", pd.Timestamp("2024-01-01", tz="UTC")],
        }
    )
    filtered = safe_listing_filter(df, days=180)
    assert "0001" in filtered["Symbol"].tolist()
