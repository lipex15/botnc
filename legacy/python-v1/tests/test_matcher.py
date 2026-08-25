import cv2
import numpy as np

from nightcrows_bot.vision.matcher import TemplateMatcher


def test_matcher_returns_full_screen_coordinates_for_a_region(tmp_path) -> None:
    rng = np.random.default_rng(42)
    template = rng.integers(0, 256, size=(12, 18, 3), dtype=np.uint8)
    template_path = tmp_path / "template.png"
    cv2.imwrite(str(template_path), template)

    frame = np.zeros((120, 180, 3), dtype=np.uint8)
    frame[55:67, 93:111] = template

    result = TemplateMatcher().find(
        frame,
        template_path,
        confidence=0.99,
        region=(70, 40, 70, 50),
    )

    assert result.found
    assert result.center is not None
    assert (result.center.x, result.center.y) == (102, 61)


def test_bright_mask_ignores_background_change(tmp_path) -> None:
    template = np.full((24, 24, 3), 25, dtype=np.uint8)
    cv2.line(template, (5, 5), (18, 5), (245, 245, 245), 2)
    cv2.line(template, (5, 12), (18, 12), (245, 245, 245), 2)
    cv2.line(template, (5, 19), (18, 19), (245, 245, 245), 2)
    template_path = tmp_path / "bright-icon.png"
    cv2.imwrite(str(template_path), template)

    frame = np.full((60, 60, 3), (120, 45, 15), dtype=np.uint8)
    frame[18:42, 20:44] = np.full((24, 24, 3), (120, 45, 15), dtype=np.uint8)
    cv2.line(frame, (25, 23), (38, 23), (245, 245, 245), 2)
    cv2.line(frame, (25, 30), (38, 30), (245, 245, 245), 2)
    cv2.line(frame, (25, 37), (38, 37), (245, 245, 245), 2)

    result = TemplateMatcher().find(
        frame,
        template_path,
        confidence=0.95,
        bright_mask=True,
    )

    assert result.found
