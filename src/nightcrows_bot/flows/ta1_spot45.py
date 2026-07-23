from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from nightcrows_bot.core.config import PROJECT_ROOT, AppConfig
from nightcrows_bot.core.models import MatchResult, ScreenPoint
from nightcrows_bot.input.windows import WindowsInput
from nightcrows_bot.vision.capture import ScreenCapture
from nightcrows_bot.vision.matcher import TemplateMatcher


TEMPLATE_ROOT = PROJECT_ROOT / "assets" / "templates" / "farm" / "ta1_spot45"


class FlowCancelled(RuntimeError):
    """Interrupção solicitada pelo usuário."""


class FlowError(RuntimeError):
    """Falha segura em uma etapa visual."""


@dataclass(frozen=True, slots=True)
class VisualTarget:
    name: str
    filename: str
    region: tuple[int, int, int, int]
    confidence: float = 0.82
    bright_mask: bool = False

    @property
    def path(self) -> Path:
        return TEMPLATE_ROOT / self.filename


MENU_BUTTON = VisualTarget(
    "botão Menu",
    "main_hud_menu.png",
    (1820, 10, 100, 110),
    confidence=0.82,
    bright_mask=True,
)
MAIN_HUD = VisualTarget(
    "HUD principal",
    "main_hud_m.png",
    (0, 850, 80, 90),
    confidence=0.78,
)
TA_MENU = VisualTarget("opção T.A.", "menu_ta.png", (1700, 290, 130, 160), confidence=0.86)
ENTER_TA1 = VisualTarget(
    "entrada Kildebat 25.000",
    "enter_ta1.png",
    (450, 680, 330, 130),
    confidence=0.84,
)
TA1_ARRIVAL = VisualTarget(
    "área Terra Avassaladora",
    "ta1_arrival.png",
    (0, 130, 320, 130),
    confidence=0.78,
)
MAP_OPEN = VisualTarget("tela Mapa", "map_open.png", (0, 0, 240, 100), confidence=0.86)
ARENA_45_ROW = VisualTarget(
    "Arena de Treinamento Nv. 45",
    "arena45_row.png",
    (1540, 340, 380, 150),
    confidence=0.78,
)
ARENA_SELECTED = VisualTarget(
    "Arena de Treinamento selecionada",
    "arena_selected.png",
    (0, 60, 360, 100),
    confidence=0.82,
)
GO_BUTTON = VisualTarget("botão Ir", "go_button.png", (780, 360, 320, 220), confidence=0.82)
AUTO_ACTIVE = VisualTarget(
    "Auto ativo",
    "auto_active.png",
    (1800, 680, 120, 180),
    confidence=0.78,
)
REST_MODE = VisualTarget(
    "modo de repouso",
    "rest_mode.png",
    (720, 820, 500, 140),
    confidence=0.80,
)

ALL_TARGETS = (
    MAIN_HUD,
    MENU_BUTTON,
    TA_MENU,
    ENTER_TA1,
    TA1_ARRIVAL,
    MAP_OPEN,
    ARENA_45_ROW,
    ARENA_SELECTED,
    GO_BUTTON,
    AUTO_ACTIVE,
    REST_MODE,
)


class TA1Spot45Flow:
    """Navega visualmente até o Spot 45 e inicia o farm em repouso."""

    def __init__(
        self,
        config: AppConfig,
        stop_event: threading.Event,
        pause_event: threading.Event,
        log: Callable[[str], None],
    ) -> None:
        self.config = config
        self.stop_event = stop_event
        self.pause_event = pause_event
        self.log = log
        self.capture = ScreenCapture(config.screen.monitor)
        self.matcher = TemplateMatcher()
        self.input = WindowsInput(config.run.simulation_mode)
        self.poll_seconds = max(0.1, config.vision.poll_interval_ms / 1000)

    def run(self) -> None:
        self._validate_assets()
        self.log(
            f"A tela do jogo deve ficar visível. Início em "
            f"{self.config.run.start_delay_seconds} segundos..."
        )
        self._wait(float(self.config.run.start_delay_seconds))

        self._wait_for(MAIN_HUD, timeout=12)
        menu = self._wait_for(MENU_BUTTON, timeout=12)
        if self.config.run.simulation_mode:
            assert menu.center is not None
            self.log(
                "Simulação concluída: botão Menu reconhecido em "
                f"({menu.center.x}, {menu.center.y}); nenhum clique foi enviado."
            )
            return

        menu_ta = self._find_once(TA_MENU)
        if menu_ta.found:
            self.log("O Menu já estava aberto.")
        else:
            self._click_match(menu, "Abrindo o Menu")
            menu_ta = self._wait_for(TA_MENU, timeout=12)
        self._click_match(menu_ta, "Abrindo T.A.")
        self._click_match(
            self._wait_for(ENTER_TA1, timeout=15),
            "Entrando na T.A 1 — Kildebat",
        )

        self._wait_for(TA1_ARRIVAL, timeout=60)
        self.log("Entrada na T.A 1 confirmada.")

        self.input.press("m")
        self.log("Abrindo o mapa com M.")
        self._wait_for(MAP_OPEN, timeout=15)

        arena = self._wait_for(ARENA_45_ROW, timeout=15)
        self._click_match(arena, "Selecionando Arena de Treinamento Nv. 45")
        self._wait_for(ARENA_SELECTED, timeout=12)

        spot_point = ScreenPoint(885, 545)
        self.input.click(spot_point)
        self.log("Marcando o ponto de chegada próximo ao Spot 45.")
        go_button = self._wait_for(GO_BUTTON, timeout=12)
        self._click_match(go_button, "Iniciando o trajeto com Ir")

        self._wait(1.2)
        self.input.press("m")
        self.log("Fechando o mapa com M.")
        self._wait_for(MAIN_HUD, timeout=15)

        self._wait_for_travel_end()

        if not self._find_once(AUTO_ACTIVE).found:
            self.input.press("q")
            self.log("Ativando o ataque automático com Q.")
            self._wait_for(AUTO_ACTIVE, timeout=15)
        else:
            self.log("O ataque automático já estava ativo; Q não foi pressionado.")

        self.input.press("l")
        self.log("Ativando o modo de repouso com L.")
        self._wait_for(REST_MODE, timeout=15)
        self.log("Farm no Spot 45 iniciado e modo de repouso confirmado.")

    def _validate_assets(self) -> None:
        missing = [target.path.name for target in ALL_TARGETS if not target.path.exists()]
        if missing:
            raise FlowError(f"Modelos visuais ausentes: {', '.join(missing)}")

    def _find_once(self, target: VisualTarget) -> MatchResult:
        return self._match(self.capture.grab(), target)

    def _match(self, frame: np.ndarray, target: VisualTarget) -> MatchResult:
        return self.matcher.find(
            frame,
            target.path,
            confidence=target.confidence,
            region=target.region,
            bright_mask=target.bright_mask,
        )

    def _wait_for(self, target: VisualTarget, timeout: float) -> MatchResult:
        self.log(f"Procurando {target.name}...")
        remaining = timeout
        best_score = 0.0
        last_frame: np.ndarray | None = None
        while remaining > 0:
            self._checkpoint()
            last_frame = self.capture.grab()
            result = self._match(last_frame, target)
            best_score = max(best_score, result.confidence)
            if result.found:
                self.log(f"{target.name.capitalize()} confirmado ({result.confidence:.0%}).")
                return result
            interval = min(self.poll_seconds, remaining)
            self._wait(interval)
            remaining -= interval
        debug_path = self._save_failure_region(last_frame, target)
        raise FlowError(
            f"Tempo esgotado procurando {target.name}. "
            f"Melhor confiança observada: {best_score:.0%}. "
            f"Captura de diagnóstico: {debug_path}."
        )

    def _save_failure_region(self, frame: np.ndarray | None, target: VisualTarget) -> Path:
        directory = PROJECT_ROOT / "screenshots" / "failures"
        directory.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output = directory / f"{timestamp}-{Path(target.filename).stem}.png"
        if frame is not None:
            x, y, width, height = target.region
            cv2.imwrite(str(output), frame[y : y + height, x : x + width])
        return output

    def _click_match(self, match: MatchResult, message: str) -> None:
        if match.center is None:
            raise FlowError(f"{message}: alvo visual sem coordenada.")
        self.input.click(match.center)
        self.log(f"{message}: clique em ({match.center.x}, {match.center.y}).")
        self._wait(0.8)

    def _wait_for_travel_end(self) -> None:
        self.log("Acompanhando o deslocamento até o Spot 45...")
        self._wait(10.0)
        remaining = float(self.config.run.travel_timeout_seconds)
        previous = self._minimap_signature()
        stable_samples = 0
        last_update = time.monotonic()

        while remaining > 0:
            self._wait(1.0)
            remaining -= 1.0
            current = self._minimap_signature()
            difference = float(cv2.absdiff(previous, current).mean())
            previous = current

            if difference <= 2.6:
                stable_samples += 1
            else:
                stable_samples = 0

            if stable_samples >= 5:
                self.log("Chegada ao Spot 45 detectada pela estabilização do minimapa.")
                return

            if time.monotonic() - last_update >= 10:
                self.log(f"Personagem ainda em deslocamento (variação visual {difference:.1f}).")
                last_update = time.monotonic()

        raise FlowError(
            "O personagem não apresentou chegada estável ao Spot 45 dentro do tempo limite."
        )

    def _minimap_signature(self) -> np.ndarray:
        frame = self.capture.grab()
        minimap = frame[120:258, 15:270]
        gray = cv2.cvtColor(minimap, cv2.COLOR_BGR2GRAY)
        return cv2.resize(gray, (96, 52), interpolation=cv2.INTER_AREA)

    def _wait(self, seconds: float) -> None:
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            self._checkpoint()
            time.sleep(min(0.1, max(0.0, deadline - time.monotonic())))

    def _checkpoint(self) -> None:
        if WindowsInput.emergency_stop_pressed():
            self.stop_event.set()
            raise FlowCancelled("Parada de emergência acionada com Ctrl+Shift+F12.")
        if self.stop_event.is_set():
            raise FlowCancelled("Execução interrompida pelo usuário.")
        while self.pause_event.is_set():
            if self.stop_event.wait(0.1):
                raise FlowCancelled("Execução interrompida pelo usuário.")
