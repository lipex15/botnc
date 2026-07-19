from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QObject, QTimer, Signal

from nightcrows_bot.core.config import AppConfig
from nightcrows_bot.core.models import BotStatus


class BotController(QObject):
    status_changed = Signal(str)
    log_emitted = Signal(str)
    elapsed_changed = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self.status = BotStatus.IDLE
        self.config = AppConfig()
        self._elapsed_seconds = 0
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

    def start(self, config: AppConfig, actual_size: tuple[int, int]) -> bool:
        expected_size = (config.screen.width, config.screen.height)
        if actual_size != expected_size:
            self._set_status(BotStatus.ERROR)
            self._log(
                f"Resolução inválida: detectada {actual_size[0]}×{actual_size[1]}, "
                f"esperada {expected_size[0]}×{expected_size[1]}."
            )
            return False

        self.config = config
        self._elapsed_seconds = 0
        self.elapsed_changed.emit(0)
        self._set_status(BotStatus.RUNNING)
        self._timer.start()
        mode = "SIMULAÇÃO" if config.run.simulation_mode else "REAL"
        self._log(f"Sessão iniciada em modo {mode} no perfil {config.run.spot}.")
        self._log("Aguardando a definição dos indicadores visuais para executar os fluxos.")
        return True

    def pause_or_resume(self) -> None:
        if self.status == BotStatus.RUNNING:
            self._timer.stop()
            self._set_status(BotStatus.PAUSED)
            self._log("Sessão pausada.")
        elif self.status == BotStatus.PAUSED:
            self._timer.start()
            self._set_status(BotStatus.RUNNING)
            self._log("Sessão retomada.")

    def stop(self) -> None:
        if self.status in {BotStatus.IDLE, BotStatus.ERROR}:
            self._set_status(BotStatus.IDLE)
            return
        self._timer.stop()
        self._set_status(BotStatus.IDLE)
        self._log("Sessão encerrada com segurança.")

    def _tick(self) -> None:
        self._elapsed_seconds += 1
        self.elapsed_changed.emit(self._elapsed_seconds)
        limit_seconds = self.config.run.farm_minutes * 60
        if self._elapsed_seconds >= limit_seconds:
            self._log("Tempo de farm configurado concluído.")
            self.stop()

    def _set_status(self, status: BotStatus) -> None:
        self.status = status
        self.status_changed.emit(status.value)

    def _log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_emitted.emit(f"[{timestamp}] {message}")

