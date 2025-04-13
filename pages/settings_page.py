from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QHBoxLayout,
    QPushButton,
)
from PySide6.QtGui import QFont, Qt
from PySide6.QtCore import Signal
import threading
import calibration_module
import config
from theme import ShadowHeaderLabel


class SettingsPage(QWidget):
    theme_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = ShadowHeaderLabel("Settings")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont("Arial", 20))
        layout.addWidget(header)

        theme_label = QLabel("Select Theme:")
        theme_label.setFont(QFont("Arial", 16))
        layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Purple", "Classic Dark"])
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        layout.addWidget(self.theme_combo)

        cluster_calib_label = QLabel("Cluster Craft Button Calibration:")
        cluster_calib_label.setFont(QFont("Arial", 16))
        layout.addWidget(cluster_calib_label)

        calib_layout = QHBoxLayout()
        self.cluster_calib_btn = QPushButton("Calibrate Cluster")
        self.cluster_calib_status = QLabel("<unset>")
        self.cluster_calib_btn.clicked.connect(self.calibrate_cluster_button)
        calib_layout.addWidget(self.cluster_calib_btn)
        calib_layout.addWidget(self.cluster_calib_status)
        layout.addLayout(calib_layout)

        layout.addStretch()
        self.setLayout(layout)

    def change_theme(self):
        theme_name = self.theme_combo.currentText()
        # Assuming main.py sets the stylesheet; here we just emit the signal.
        self.theme_changed.emit(theme_name)

    def calibrate_cluster_button(self):
        def task():
            pos = calibration_module.calibrate_cluster_craft_button()
            if pos:
                status = f"({pos['x']}, {pos['y']})"
                config.set_value(pos, "cluster", "button-location")
                self.cluster_calib_status.setText(status)

        threading.Thread(target=task, daemon=True).start()

    def update_theme(self, new_theme):
        # Update the style of the section container (or any other elements)
        from theme import (
            get_section_style,
        )  # assuming you centralized theming in theme.py

        # self.section_container.setStyleSheet(get_section_style(new_theme))
        # Optionally, update other widget styles if needed
