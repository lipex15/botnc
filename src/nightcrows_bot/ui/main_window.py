from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from nightcrows_bot.core.config import AppConfig, load_config, save_config
from nightcrows_bot.core.controller import BotController


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.config = load_config()
        self.controller = BotController()
        self.setWindowTitle("Night Crows Visual Automator")
        self.setMinimumSize(980, 650)
        self.resize(1120, 720)
        self._build_ui()
        self._connect_signals()
        self._load_fields()

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(24, 22, 24, 22)
        root_layout.setSpacing(18)

        header = QHBoxLayout()
        titles = QVBoxLayout()
        title = QLabel("Night Crows Automator")
        title.setObjectName("Title")
        subtitle = QLabel("Automação visual · tela fixa 1920×1080")
        subtitle.setObjectName("Subtitle")
        titles.addWidget(title)
        titles.addWidget(subtitle)
        header.addLayout(titles)
        header.addStretch()
        self.status_badge = QLabel("Parado")
        self.status_badge.setObjectName("StatusBadge")
        header.addWidget(self.status_badge)
        root_layout.addLayout(header)

        columns = QHBoxLayout()
        columns.setSpacing(18)
        columns.addWidget(self._build_settings_panel(), 4)
        columns.addWidget(self._build_runtime_panel(), 5)
        root_layout.addLayout(columns, 1)

        self.setCentralWidget(root)

    def _build_settings_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        section = QLabel("Configuração da sessão")
        section.setObjectName("Section")
        layout.addWidget(section)

        form = QFormLayout()
        form.setSpacing(13)
        self.spot = QComboBox()
        self.spot.setEditable(True)
        self.spot.addItems(["Spot 1", "Spot 2", "Spot 3"])
        form.addRow("Local de farm", self.spot)

        self.farm_minutes = self._spin(1, 1440, " min")
        form.addRow("Tempo de farm", self.farm_minutes)

        self.low_hp = self._spin(1, 99, "%")
        form.addRow("Retornar com vida", self.low_hp)

        self.max_deaths = self._spin(1, 100, " mortes")
        form.addRow("Limite de mortes", self.max_deaths)

        self.agenda_minutes = self._spin(1, 1440, " min")
        form.addRow("Tempo na agenda", self.agenda_minutes)
        layout.addLayout(form)

        self.simulation = QCheckBox("Modo de simulação (sem cliques)")
        self.simulation.setToolTip("Mantenha ativado enquanto os fluxos estão sendo configurados.")
        layout.addWidget(self.simulation)
        layout.addStretch()

        note = QLabel(
            "Os módulos de farm, HP, poção, morte e agenda serão ativados conforme "
            "recebermos seus indicadores visuais."
        )
        note.setWordWrap(True)
        note.setObjectName("Subtitle")
        layout.addWidget(note)
        return panel

    def _build_runtime_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        top = QHBoxLayout()
        section = QLabel("Execução")
        section.setObjectName("Section")
        self.elapsed = QLabel("00:00:00")
        self.elapsed.setAlignment(Qt.AlignmentFlag.AlignRight)
        top.addWidget(section)
        top.addStretch()
        top.addWidget(self.elapsed)
        layout.addLayout(top)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("As decisões e confirmações visuais aparecerão aqui.")
        layout.addWidget(self.log, 1)

        buttons = QHBoxLayout()
        self.start_button = QPushButton("Iniciar")
        self.start_button.setObjectName("Primary")
        self.pause_button = QPushButton("Pausar")
        self.pause_button.setEnabled(False)
        self.stop_button = QPushButton("Parar")
        self.stop_button.setObjectName("Danger")
        self.stop_button.setEnabled(False)
        buttons.addWidget(self.start_button, 2)
        buttons.addWidget(self.pause_button)
        buttons.addWidget(self.stop_button)
        layout.addLayout(buttons)
        return panel

    @staticmethod
    def _spin(minimum: int, maximum: int, suffix: str) -> QSpinBox:
        widget = QSpinBox()
        widget.setRange(minimum, maximum)
        widget.setSuffix(suffix)
        return widget

    def _connect_signals(self) -> None:
        self.start_button.clicked.connect(self._start)
        self.pause_button.clicked.connect(self._pause_or_resume)
        self.stop_button.clicked.connect(self.controller.stop)
        self.controller.status_changed.connect(self._status_changed)
        self.controller.log_emitted.connect(self.log.appendPlainText)
        self.controller.elapsed_changed.connect(self._elapsed_changed)

    def _load_fields(self) -> None:
        self.spot.setCurrentText(self.config.run.spot)
        self.farm_minutes.setValue(self.config.run.farm_minutes)
        self.low_hp.setValue(self.config.run.low_hp_percent)
        self.max_deaths.setValue(self.config.run.max_deaths)
        self.agenda_minutes.setValue(self.config.run.agenda_minutes)
        self.simulation.setChecked(self.config.run.simulation_mode)

    def _read_fields(self) -> AppConfig:
        self.config.run.spot = self.spot.currentText().strip() or "Spot 1"
        self.config.run.farm_minutes = self.farm_minutes.value()
        self.config.run.low_hp_percent = self.low_hp.value()
        self.config.run.max_deaths = self.max_deaths.value()
        self.config.run.agenda_minutes = self.agenda_minutes.value()
        self.config.run.simulation_mode = self.simulation.isChecked()
        return self.config

    def _start(self) -> None:
        config = self._read_fields()
        save_config(config)
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            QMessageBox.critical(self, "Tela indisponível", "Não foi possível detectar a tela principal.")
            return
        geometry = screen.geometry()
        actual_size = (geometry.width(), geometry.height())
        if not self.controller.start(config, actual_size):
            QMessageBox.warning(
                self,
                "Resolução incompatível",
                "Configure a tela principal em 1920×1080 antes de iniciar.",
            )

    def _pause_or_resume(self) -> None:
        self.controller.pause_or_resume()

    def _status_changed(self, status: str) -> None:
        self.status_badge.setText(status)
        running = status == "Executando"
        paused = status == "Pausado"
        self.start_button.setEnabled(not running and not paused)
        self.pause_button.setEnabled(running or paused)
        self.stop_button.setEnabled(running or paused)
        self.pause_button.setText("Continuar" if paused else "Pausar")

    def _elapsed_changed(self, seconds: int) -> None:
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.elapsed.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    def closeEvent(self, event) -> None:  # noqa: N802
        self.controller.stop()
        save_config(self._read_fields())
        event.accept()

