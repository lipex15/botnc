from __future__ import annotations

import mss
import numpy as np


class ScreenCapture:
    """Captura pixels da tela, sem procurar ou vincular uma janela."""

    def __init__(self, monitor: int = 1) -> None:
        self.monitor = monitor

    def grab(self) -> np.ndarray:
        with mss.mss() as capture:
            monitors = capture.monitors
            if self.monitor >= len(monitors):
                raise RuntimeError(f"Monitor {self.monitor} não está disponível.")
            frame = np.asarray(capture.grab(monitors[self.monitor]))
        return frame[:, :, :3]

    def size(self) -> tuple[int, int]:
        with mss.mss() as capture:
            monitor = capture.monitors[self.monitor]
        return int(monitor["width"]), int(monitor["height"])

