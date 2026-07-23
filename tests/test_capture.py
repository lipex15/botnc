from nightcrows_bot.vision.capture import ScreenCapture


def test_primary_monitor_is_selected_explicitly() -> None:
    monitors = [
        {"left": -1920, "top": 0, "width": 3840, "height": 1080},
        {
            "left": -1920,
            "top": 0,
            "width": 1920,
            "height": 1080,
            "is_primary": False,
        },
        {
            "left": 0,
            "top": 0,
            "width": 1920,
            "height": 1080,
            "is_primary": True,
        },
    ]

    selected = ScreenCapture(primary_only=True)._select_monitor(monitors)

    assert selected["left"] == 0
    assert selected["is_primary"] is True
