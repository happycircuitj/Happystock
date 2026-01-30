"""Jupyter widget UI for the scanner."""
from __future__ import annotations

from typing import List

from divergence_scanner.ui.preset_manager import PresetManager


class DivergenceScannerUI:
    def __init__(self) -> None:
        self.presets = PresetManager()

    def create_widget_interface(self):
        """Create interactive widget controls.

        Returns:
            Widget layout container.
        """
        try:
            import ipywidgets as widgets
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ImportError("ipywidgets is required for the UI") from exc

        preset_dropdown = widgets.Dropdown(
            options=["탐색형", "확정형", "리스크온", "리스크오프"],
            value="확정형",
        )
        lookback_slider = widgets.IntSlider(
            value=45, min=20, max=120, step=5, description="Lookback Period"
        )
        run_button = widgets.Button(description="Run Scan")
        output_area = widgets.Output()
        return self._create_layout([preset_dropdown, lookback_slider, run_button, output_area])

    def _create_layout(self, widgets_list: List) -> object:
        import ipywidgets as widgets

        return widgets.VBox(widgets_list)
