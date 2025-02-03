import sys
import json
import threading
import time
import os

if sys.platform == "win32":
    import ctypes

    # Set DPI awareness on Windows
    ctypes.windll.user32.SetProcessDPIAware = (
        lambda: None
    )  # pyright: ignore[reportAttributeAccessIssue]
    ctypes.windll.shcore.SetProcessDpiAwareness = (
        lambda _: None
    )  # pyright: ignore[reportUnknownLambdaType]

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QFrame,
    QStackedWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
)
from PySide6.QtGui import QFont

# Import pages from the pages subpackage
from pages.calibration_page import CalibrationPage
from pages.clusters_page import ClustersPage
from pages.maps_page import MapsPage
from pages.items_page import ItemsPage
from pages.settings_page import SettingsPage

import config
from theme import (
    get_stylesheet,
    get_button_style,
    get_section_style,
)  # New import from theme.py


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Odin - PySide6 Version")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()
        self.load_positions()

    def init_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout()

        # Sidebar using QPushButtons for navigation.
        sidebar = QFrame()
        sidebar.setFrameShape(QFrame.StyledPanel)
        sidebar_layout = QVBoxLayout()

        # Create sidebar buttons with rounded styling.
        button_style = """
            QPushButton {
                background-color: #4b0082;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5d00a0;
            }
        """

        self.home_btn = QPushButton("Home")
        self.home_btn.setStyleSheet(button_style)
        self.home_btn.clicked.connect(lambda: self.switch_page(0))
        sidebar_layout.addWidget(self.home_btn)

        self.clusters_btn = QPushButton("Clusters")
        self.clusters_btn.setStyleSheet(button_style)
        self.clusters_btn.clicked.connect(lambda: self.switch_page(1))
        sidebar_layout.addWidget(self.clusters_btn)

        self.maps_btn = QPushButton("Maps")
        self.maps_btn.setStyleSheet(button_style)
        self.maps_btn.clicked.connect(lambda: self.switch_page(2))
        sidebar_layout.addWidget(self.maps_btn)

        self.items_btn = QPushButton("Items")
        self.items_btn.setStyleSheet(button_style)
        self.items_btn.clicked.connect(lambda: self.switch_page(3))
        sidebar_layout.addWidget(self.items_btn)

        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setStyleSheet(button_style)
        self.settings_btn.clicked.connect(lambda: self.switch_page(4))
        sidebar_layout.addWidget(self.settings_btn)

        self.killswitch_label = QLabel("Killswitch: OFF")
        sidebar_layout.addWidget(self.killswitch_label)
        sidebar_layout.addStretch()
        sidebar.setLayout(sidebar_layout)

        # Pages
        self.pages = QStackedWidget()
        self.calibration_page = CalibrationPage()
        self.clusters_page = ClustersPage()
        self.maps_page = MapsPage()
        self.items_page = ItemsPage()
        self.settings_page = SettingsPage()

        # Connect theme change signal to propagate changes.
        self.settings_page.theme_changed.connect(self.on_theme_changed)

        self.pages.addWidget(self.calibration_page)
        self.pages.addWidget(self.clusters_page)
        self.pages.addWidget(self.maps_page)
        self.pages.addWidget(self.items_page)
        self.pages.addWidget(self.settings_page)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def load_positions(self):
        cluster_pos = config.get_value("cluster", "button-location")
        if cluster_pos:
            self.settings_page.cluster_calib_status.setText(
                f"({cluster_pos['x']}, {cluster_pos['y']})"
            )
        for key, label in self.calibration_page.currency_labels.items():
            pos = config.get_value("currency", key)
            if pos:
                label.setText(f"({pos['x']}, {pos['y']})")

    def on_theme_changed(self, theme_name):
        # Update the application's stylesheet so the program's background and widget styles change.
        stylesheet = get_stylesheet(theme_name)
        QApplication.instance().setStyleSheet(stylesheet)

        # Propagate the theme change to all pages that have an update_theme() method.
        self.calibration_page.update_theme(theme_name)
        self.items_page.update_theme(theme_name)
        # Update sidebar buttons if needed
        button_style = get_button_style(theme_name)
        self.home_btn.setStyleSheet(button_style)
        self.clusters_btn.setStyleSheet(button_style)
        self.maps_btn.setStyleSheet(button_style)
        self.items_btn.setStyleSheet(button_style)
        self.settings_btn.setStyleSheet(button_style)

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(get_stylesheet("Dark Purple"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
