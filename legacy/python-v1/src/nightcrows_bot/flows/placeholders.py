from __future__ import annotations

from nightcrows_bot.core.models import FlowKind
from nightcrows_bot.flows.base import FlowContext, VisualFlow


class PendingVisualFlow(VisualFlow):
    """Reserva um fluxo até que seus indicadores visuais sejam fornecidos."""

    def __init__(self, kind: FlowKind) -> None:
        self.kind = kind

    def can_run(self, context: FlowContext) -> bool:
        return False

    def run(self, context: FlowContext) -> None:
        raise RuntimeError(f"O fluxo '{self.kind.value}' ainda não foi configurado.")


def initial_flows() -> list[PendingVisualFlow]:
    return [PendingVisualFlow(kind) for kind in FlowKind]

