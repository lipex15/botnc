from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from nightcrows_bot.ui.main_window import MainWindow
from nightcrows_bot.ui.theme import APP_STYLE


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Night Crows Visual Automator")
    app.setStyleSheet(APP_STYLE)
    window = MainWindow()
    window.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()

