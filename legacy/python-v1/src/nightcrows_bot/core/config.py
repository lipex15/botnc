from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "default.json"
USER_CONFIG_PATH = PROJECT_ROOT / "config" / "user.json"


@dataclass(slots=True)
class ScreenConfig:
    width: int = 1920
    height: int = 1080
    monitor: int = 1
    primary_only: bool = True


@dataclass(slots=True)
class RunConfig:
    spot: str = "T.A 1 — Spot 45"
    farm_minutes: int = 60
    low_hp_percent: int = 25
    max_deaths: int = 3
    agenda_minutes: int = 30
    simulation_mode: bool = True
    start_delay_seconds: int = 3
    travel_timeout_seconds: int = 120


@dataclass(slots=True)
class VisionConfig:
    default_confidence: float = 0.88
    poll_interval_ms: int = 500


@dataclass(slots=True)
class AppConfig:
    screen: ScreenConfig = field(default_factory=ScreenConfig)
    run: RunConfig = field(default_factory=RunConfig)
    vision: VisionConfig = field(default_factory=VisionConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppConfig":
        return cls(
            screen=ScreenConfig(**data.get("screen", {})),
            run=RunConfig(**data.get("run", {})),
            vision=VisionConfig(**data.get("vision", {})),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_config() -> AppConfig:
    source = USER_CONFIG_PATH if USER_CONFIG_PATH.exists() else DEFAULT_CONFIG_PATH
    if not source.exists():
        return AppConfig()
    return AppConfig.from_dict(json.loads(source.read_text(encoding="utf-8")))


def save_config(config: AppConfig) -> None:
    USER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    USER_CONFIG_PATH.write_text(
        json.dumps(config.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
