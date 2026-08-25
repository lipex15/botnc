from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from nightcrows_bot.core.models import FlowKind


@dataclass(slots=True)
class FlowContext:
    deaths: int = 0
    hp_potions_available: bool = True
    low_hp_detected: bool = False


class VisualFlow(ABC):
    kind: FlowKind

    @abstractmethod
    def can_run(self, context: FlowContext) -> bool:
        """Informa se o fluxo deve assumir o controle."""

    @abstractmethod
    def run(self, context: FlowContext) -> None:
        """Executa o fluxo e confirma visualmente o resultado."""

