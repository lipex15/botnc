from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BotStatus(str, Enum):
    IDLE = "Parado"
    RUNNING = "Executando"
    PAUSED = "Pausado"
    STOPPING = "Parando"
    ERROR = "Erro"


class FlowKind(str, Enum):
    FARM = "Farm"
    LOW_HP_RETURN = "Retorno por vida baixa"
    BUY_HP_POTION = "Compra de poção de HP"
    DEATH_RECOVERY = "Recuperação após morte"
    AGENDA = "Agenda"


@dataclass(frozen=True, slots=True)
class ScreenPoint:
    x: int
    y: int


@dataclass(frozen=True, slots=True)
class MatchResult:
    found: bool
    confidence: float
    center: ScreenPoint | None = None

