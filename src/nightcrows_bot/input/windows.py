from __future__ import annotations

import ctypes
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
        if not (0 <= point.x < 1920 and 0 <= point.y < 1080):
            raise ValueError(f"Clique fora da tela permitida: ({point.x}, {point.y})")
        pyautogui.moveTo(point.x, point.y, duration=duration)
        pyautogui.click()

    def press(self, key: str) -> None:
        if self.simulation_mode:
            return
        pyautogui.press(key)

    @staticmethod
    def emergency_stop_pressed() -> bool:
        """Ctrl+Shift+F12 funciona mesmo com o aplicativo minimizado."""
        user32 = ctypes.windll.user32
        keys = (0x11, 0x10, 0x7B)  # Ctrl, Shift e F12
        return all(bool(user32.GetAsyncKeyState(key) & 0x8000) for key in keys)

    def wait(self, seconds: float) -> None:
        time.sleep(seconds)
