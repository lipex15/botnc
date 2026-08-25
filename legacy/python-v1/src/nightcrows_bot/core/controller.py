from __future__ import annotations

import threading
from datetime import datetime

from PySide6.QtCore import QObject, QTimer, Signal

from nightcrows_bot.core.config import AppConfig
from nightcrows_bot.core.models import BotStatus
from nightcrows_bot.flows.ta1_spot45 import FlowCancelled, TA1Spot45Flow


class BotController(QObject):
    status_changed = Signal(str)
    log_emitted = Signal(str)
    elapsed_changed = Signal(int)
    run_finished = Signal(bool, str)
    _worker_finished = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()
        self.status = BotStatus.IDLE
        self.config = AppConfig()
        self._elapsed_seconds = 0
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._worker: threading.Thread | None = None
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)
        self._worker_finished.connect(self._finish_from_worker)

    def start(self, config: AppConfig, actual_size: tuple[int, int]) -> bool:
        if self._worker is not None and self._worker.is_alive():
            self._log("Já existe uma execução em andamento.")
            return False

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
        self._stop_event.clear()
        self._pause_event.clear()
        self.elapsed_changed.emit(0)
        self._set_status(BotStatus.RUNNING)
        self._timer.start()

        mode = "SIMULAÇÃO" if config.run.simulation_mode else "REAL"
        self._log(f"Sessão iniciada em modo {mode}: {config.run.spot}.")
        self._worker = threading.Thread(
            target=self._run_flow,
            name="ta1-spot45-flow",
            daemon=True,
        )
        self._worker.start()
        return True

    def pause_or_resume(self) -> None:
        if self.status == BotStatus.RUNNING:
            self._pause_event.set()
            self._timer.stop()
            self._set_status(BotStatus.PAUSED)
            self._log("Sessão pausada.")
        elif self.status == BotStatus.PAUSED:
            self._pause_event.clear()
            self._timer.start()
            self._set_status(BotStatus.RUNNING)
            self._log("Sessão retomada.")

    def stop(self) -> None:
        if self.status not in {BotStatus.RUNNING, BotStatus.PAUSED, BotStatus.STOPPING}:
            return
        self._stop_event.set()
        self._pause_event.clear()
        self._timer.stop()
        self._set_status(BotStatus.STOPPING)
        self._log("Parada solicitada; aguardando a etapa atual encerrar.")

    def _run_flow(self) -> None:
        try:
            TA1Spot45Flow(
                config=self.config,
                stop_event=self._stop_event,
                pause_event=self._pause_event,
                log=self._log,
            ).run()
        except FlowCancelled as exc:
            self._worker_finished.emit("cancelled", str(exc))
        except Exception as exc:
            self._worker_finished.emit("error", str(exc))
        else:
            self._worker_finished.emit("success", "Fluxo concluído com sucesso.")

    def _finish_from_worker(self, outcome: str, message: str) -> None:
        self._timer.stop()
        self._worker = None
        if outcome == "success":
            self._set_status(BotStatus.COMPLETED)
            self._log(message)
            self.run_finished.emit(True, message)
        elif outcome == "cancelled":
            self._set_status(BotStatus.IDLE)
            self._log(message)
            self.run_finished.emit(False, message)
        else:
            self._set_status(BotStatus.ERROR)
            self._log(f"Fluxo interrompido com segurança: {message}")
            self.run_finished.emit(False, message)

    def _tick(self) -> None:
        self._elapsed_seconds += 1
        self.elapsed_changed.emit(self._elapsed_seconds)

    def _set_status(self, status: BotStatus) -> None:
        self.status = status
        self.status_changed.emit(status.value)

    def _log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_emitted.emit(f"[{timestamp}] {message}")
