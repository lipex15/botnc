from nightcrows_bot.core.config import AppConfig
from nightcrows_bot.core.models import BotStatus


def test_expected_resolution() -> None:
    config = AppConfig()
    assert (config.screen.width, config.screen.height) == (1920, 1080)
    assert BotStatus.IDLE.value == "Parado"
    assert BotStatus.COMPLETED.value == "Concluído"
