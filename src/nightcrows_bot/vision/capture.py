from __future__ import annotations

import mss
import numpy as np


class ScreenCapture:
    """Captura pixels da tela, sem procurar ou vincular uma janela."""

    def __init__(self, monitor: int = 1, primary_only: bool = True) -> None:
        self.monitor = monitor
        self.primary_only = primary_only

    def grab(self) -> np.ndarray:
        with mss.MSS() as capture:
            frame = np.asarray(capture.grab(self._select_monitor(capture.monitors)))
        return frame[:, :, :3]

    def size(self) -> tuple[int, int]:
        with mss.MSS() as capture:
            monitor = self._select_monitor(capture.monitors)
        return int(monitor["width"]), int(monitor["height"])

    def _select_monitor(self, monitors: list[dict]) -> dict:
        physical_monitors = monitors[1:]
        if self.primary_only:
            for monitor in physical_monitors:
                if monitor.get("is_primary"):
                    return monitor
            for monitor in physical_monitors:
                if monitor["left"] == 0 and monitor["top"] == 0:
                    return monitor
            raise RuntimeError("Não foi possível identificar o monitor principal.")

        if self.monitor <= 0 or self.monitor >= len(monitors):
            raise RuntimeError(f"Monitor {self.monitor} não está disponível.")
        return monitors[self.monitor]
