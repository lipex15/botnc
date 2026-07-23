import threading

import cv2

from nightcrows_bot.core.config import AppConfig
from nightcrows_bot.core.models import MatchResult, ScreenPoint
from nightcrows_bot.flows.ta1_spot45 import ALL_TARGETS
from nightcrows_bot.flows.ta1_spot45 import TA1Spot45Flow


def test_all_ta1_spot45_templates_exist_and_fit_search_regions() -> None:
    for target in ALL_TARGETS:
        assert target.path.exists(), target.path
        template = cv2.imread(str(target.path), cv2.IMREAD_COLOR)
        assert template is not None
        template_height, template_width = template.shape[:2]
        _, _, region_width, region_height = target.region
        assert template_width <= region_width
        assert template_height <= region_height


def test_all_search_regions_fit_full_hd() -> None:
    for target in ALL_TARGETS:
        x, y, width, height = target.region
        assert x >= 0 and y >= 0
        assert x + width <= 1920
        assert y + height <= 1080


def test_real_flow_keeps_the_expected_action_order(monkeypatch) -> None:
    class FakeInput:
        def __init__(self) -> None:
            self.clicks: list[ScreenPoint] = []
            self.keys: list[str] = []

        def click(self, point: ScreenPoint, duration: float = 0.15) -> None:
            self.clicks.append(point)

        def press(self, key: str) -> None:
            self.keys.append(key)

    config = AppConfig()
    config.run.simulation_mode = False
    config.run.start_delay_seconds = 0
    flow = TA1Spot45Flow(
        config=config,
        stop_event=threading.Event(),
        pause_event=threading.Event(),
        log=lambda _message: None,
    )
    fake_input = FakeInput()
    flow.input = fake_input

    monkeypatch.setattr(flow, "_validate_assets", lambda: None)
    monkeypatch.setattr(flow, "_wait", lambda _seconds: None)
    monkeypatch.setattr(flow, "_wait_for_travel_end", lambda: None)
    monkeypatch.setattr(
        flow,
        "_wait_for",
        lambda _target, timeout: MatchResult(
            found=True,
            confidence=1.0,
            center=ScreenPoint(100, 200),
        ),
    )
    monkeypatch.setattr(
        flow,
        "_find_once",
        lambda _target: MatchResult(found=False, confidence=0.2),
    )

    flow.run()

    assert fake_input.keys == ["m", "m", "q", "l"]
    assert fake_input.clicks == [
        ScreenPoint(100, 200),
        ScreenPoint(100, 200),
        ScreenPoint(100, 200),
        ScreenPoint(100, 200),
        ScreenPoint(885, 545),
        ScreenPoint(100, 200),
    ]
