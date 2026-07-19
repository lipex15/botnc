from nightcrows_bot.core.config import AppConfig


def test_default_resolution_is_fixed_to_full_hd() -> None:
    config = AppConfig()
    assert (config.screen.width, config.screen.height) == (1920, 1080)


def test_config_round_trip() -> None:
    config = AppConfig()
    config.run.spot = "Mina Norte"
    config.run.max_deaths = 4

    restored = AppConfig.from_dict(config.to_dict())

    assert restored.run.spot == "Mina Norte"
    assert restored.run.max_deaths == 4
    assert restored.run.simulation_mode is True

