from __future__ import annotations

import time

import pyautogui

from nightcrows_bot.core.models import ScreenPoint


class WindowsInput:
    """Envia ações normais ao Windows e respeita o modo de simulação."""

    def __init__(self, simulation_mode: bool = True) -> None:
        self.simulation_mode = simulation_mode
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.08

    def click(self, point: ScreenPoint, duration: float = 0.15) -> None:
        if self.simulation_mode:
            return
        pyautogui.moveTo(point.x, point.y, duration=duration)
        pyautogui.click()

    def press(self, key: str) -> None:
        if self.simulation_mode:
            return
        pyautogui.press(key)

    def wait(self, seconds: float) -> None:
        time.sleep(seconds)

