import sys

if sys.platform == "win32":
    import ctypes

    # Set DPI awareness on Windows
    ctypes.windll.user32.SetProcessDPIAware = (
        lambda: None
    )  # pyright: ignore[reportAttributeAccessIssue]
    ctypes.windll.shcore.SetProcessDpiAwareness = (
        lambda _: None
    )  # pyright: ignore[reportUnknownLambdaType]

import json
import threading
import time
import os

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QCheckBox,
    QSpinBox,
    QFileDialog,
    QFrame,
    QMessageBox,
    QComboBox,
    QGridLayout,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QObject, QTimer
from PySide6.QtGui import QPixmap, QFont, QCursor
from PySide6.QtWidgets import QToolTip

import calibration_module
import cluster_module
import item_craft_module
import map_module
import bot_controller
import config
from mytypes import Position, Cluster  # renamed module


# ------------------------------------------------------------------------------
# Theme helper: returns a stylesheet string for each theme.
def get_stylesheet(theme_name: str) -> str:
    themes = {
        "Dark Purple": """
        QWidget {
            background-color: #2e003e;
            color: #ffffff;
        }
        QPushButton {
            background-color: #4b0082;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 8px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #5d00a0;
        }
        QLabel {
            color: #ffffff;
        }
        QLineEdit, QSpinBox, QComboBox {
            background-color: #3a004d;
            color: #ffffff;
            border: 1px solid #4b0082;
        }
        """,
        "Dark Amber": """
        QWidget {
            background-color: #3e2c1d;
            color: #f0e68c;
        }
        QPushButton {
            background-color: #ffbf00;
            color: #000000;
            border: none;
            border-radius: 8px;
            padding: 8px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #e0ac00;
        }
        QLabel {
            color: #f0e68c;
        }
        QLineEdit, QSpinBox, QComboBox {
            background-color: #4e3621;
            color: #f0e68c;
            border: 1px solid #ffbf00;
        }
        """,
        "Classic Dark": """
        QWidget {
            background-color: #222222;
            color: #ffffff;
        }
        QPushButton {
            background-color: #444444;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 8px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #555555;
        }
        QLabel {
            color: #ffffff;
        }
        QLineEdit, QSpinBox, QComboBox {
            background-color: #333333;
            color: #ffffff;
            border: 1px solid #444444;
        }
        """,
    }
    return themes.get(theme_name, "")


# ------------------------------------------------------------------------------
# Container style helper.
def get_container_style(theme="Dark Purple"):
    if theme == "Dark Purple":
        return "background-color: #2e003e; border: 1px solid #5e085e; border-radius: 4px; padding: 4px;"
    elif theme == "Dark Amber":
        return "background-color: #3e2c1d; border: 1px solid #ffbf00; border-radius: 4px; padding: 4px;"
    elif theme == "Classic Dark":
        return "background-color: #222222; border: 1px solid #444444; border-radius: 4px; padding: 4px;"
    else:
        return "background-color: #2c2c2c; border: 1px solid #555555; border-radius: 4px; padding: 4px;"


# ------------------------------------------------------------------------------
# Section style helper for ItemsPage settings.
def get_section_style(theme="Dark Purple"):
    if theme == "Dark Purple":
        border_color = "#5e085e"
        background_color = "#2e003e"
    elif theme == "Dark Amber":
        border_color = "#ffbf00"
        background_color = "#3e2c1d"
    elif theme == "Classic Dark":
        border_color = "#444444"
        background_color = "#222222"
    else:
        border_color = "#555555"
        background_color = "#2c2c2c"
    return f"background-color: {background_color}; border: 2px solid {border_color}; border-radius: 8px; padding: 4px;"


# ------------------------------------------------------------------------------
# SettingsPage.
class SettingsPage(QWidget):
    theme_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QLabel("Settings")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 20))
        layout.addWidget(header)

        theme_label = QLabel("Select Theme:")
        theme_label.setFont(QFont("Arial", 16))
        layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Purple", "Dark Amber", "Classic Dark"])
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
        stylesheet = get_stylesheet(theme_name)
        QApplication.instance().setStyleSheet(stylesheet)
        self.theme_changed.emit(theme_name)

    def calibrate_cluster_button(self):
        def task():
            pos = calibration_module.calibrate_cluster_craft_button()
            status = f"({pos['x']}, {pos['y']})"
            config.set_value(pos, "cluster", "button-location")
            self.cluster_calib_status.setText(status)

        threading.Thread(target=task, daemon=True).start()


# ------------------------------------------------------------------------------
# KillswitchMonitor.
class KillswitchMonitor(QObject):
    killswitch_toggled = Signal(bool)

    def __init__(self):
        super().__init__()
        self.start_monitor()

    def start_monitor(self):
        import keyboard

        def monitor():
            while True:
                keyboard.wait("+")
                bot_controller.Bot.toggle_killswitch()
                self.killswitch_toggled.emit(bot_controller.Bot.get_killswitch_state())

        threading.Thread(target=monitor, daemon=True).start()


# ------------------------------------------------------------------------------
# CalibrationPage.
class CalibrationPage(QWidget):
    def __init__(self):
        super().__init__()
        self.containers = []
        self.currency_buttons = {}
        self.currency_labels = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        header = QLabel("Calibration")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 20))
        main_layout.addWidget(header)

        currencies = {
            "chaos": ("Chaos Orb", "chaos.png"),
            "exalted": ("Exalted Orb", "exalted.png"),
            "ancient": ("Ancient Orb", "ancient.png"),
            "transmutation": ("Orb of Transmutation", "transmutation.png"),
            "augment": ("Orb of Augmentation", "augment.png"),
            "alteration": ("Orb of Alteration", "alteration.png"),
            "alchemy": ("Orb of Alchemy", "alchemy.png"),
            "regal": ("Regal Orb", "regal.png"),
            "scouring": ("Orb of Scouring", "scouring.png"),
            "vaal": ("Vaal Orb", "vaal.png"),
            "blessed": ("Blessed Orb", "blessed.png"),
            "cartographer": ("Cartographer's Chisel", "cartographer.png"),
        }

        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(5, 5, 5, 5)
        grid_layout.setSpacing(10)
        num_columns = 3

        for index, (key, (display_name, img_file)) in enumerate(currencies.items()):
            row = index // num_columns
            col = index % num_columns

            container = QWidget()
            container_layout = QHBoxLayout()
            container_layout.setContentsMargins(2, 2, 2, 2)
            container_layout.setSpacing(2)

            btn = QPushButton(display_name)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            container_layout.addWidget(btn)
            container_layout.addSpacing(2)

            img_path = os.path.join("images", img_file)
            img_label = QLabel()
            if os.path.exists(img_path):
                pixmap = QPixmap(img_path).scaled(
                    39, 39, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                img_label.setPixmap(pixmap)
            else:
                img_label.setText(display_name)
            img_label.setFixedWidth(45)
            container_layout.addWidget(img_label)
            container_layout.addSpacing(2)

            status = QLabel("???")
            status.setAlignment(Qt.AlignCenter)
            fixed_width = status.fontMetrics().horizontalAdvance("XXXXXXXXXXXX")
            status.setFixedWidth(fixed_width)
            container_layout.addWidget(status)

            container.setLayout(container_layout)
            container.setStyleSheet(get_container_style("Dark Purple"))
            self.containers.append(container)
            grid_layout.addWidget(container, row, col)

            btn.clicked.connect(
                lambda checked, cur=key, lbl=status: self.calibrate_currency(cur, lbl)
            )
            self.currency_buttons[key] = btn
            self.currency_labels[key] = status

        main_layout.addLayout(grid_layout)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def calibrate_currency(self, currency, label_widget):
        def task():
            pos = calibration_module.calibrate(currency)
            status = f"({pos['x']}, {pos['y']})"
            config.set_value(pos, "currency", currency)
            label_widget.setText(status)

        threading.Thread(target=task, daemon=True).start()

    def update_theme(self, new_theme):
        new_style = get_container_style(new_theme)
        for container in self.containers:
            container.setStyleSheet(new_style)


# ------------------------------------------------------------------------------
# CraftedJewelWidget: A widget representing a crafted cluster jewel.
class PersistentTooltip(QWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent, Qt.ToolTip)
        self.label = QLabel(text, self)
        self.label.setStyleSheet(
            "background-color: rgba(0, 0, 0, 200); color: white; padding: 4px; border-radius: 4px;"
        )
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.adjustSize()

    def setText(self, text: str):
        self.label.setText(text)
        self.adjustSize()


class CraftedJewelWidget(QWidget):
    def __init__(self, cluster):
        super().__init__()
        self.cluster = cluster
        self.setFixedSize(39, 39)
        image_file = f"images/{cluster.jewel_type.lower().replace(' ', '_')}.png"
        self.pixmap = QPixmap(image_file).scaled(
            39, 39, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.tooltip = None  # Will hold our persistent tooltip

    def paintEvent(self, event):
        from PySide6.QtWidgets import QStylePainter

        painter = QStylePainter(self)
        if not self.pixmap.isNull():
            painter.drawPixmap(0, 0, self.pixmap)
        else:
            painter.drawText(self.rect(), Qt.AlignCenter, "?")

    def buildTooltipText(self) -> str:
        text = f"<b>Item Info:</b><br>"
        text += f"Item Level: {self.cluster.ilvl}<br>"
        text += f"Passives: {self.cluster.passives}<br>"
        text += f"Jewel Type: {self.cluster.jewel_type}<br><br>"
        text += "<b>Mods:</b><br>" + "<br>".join(self.cluster.mods)
        return text

    def enterEvent(self, event):
        # Create and show the persistent tooltip
        tooltip_text = self.buildTooltipText()
        self.tooltip = PersistentTooltip(tooltip_text, self.window())
        # Position the tooltip relative to the widget. Adjust offsets as needed.
        global_pos = self.mapToGlobal(self.rect().bottomLeft())
        # Here, we shift the tooltip up if it would hang off the window.
        window_geom = self.window().geometry()
        tooltip_height = self.tooltip.height()
        if global_pos.y() + tooltip_height > window_geom.bottom():
            global_pos.setY(window_geom.bottom() - tooltip_height - 5)
        self.tooltip.move(global_pos)
        self.tooltip.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.tooltip:
            self.tooltip.hide()
            self.tooltip.deleteLater()
            self.tooltip = None
        super().leaveEvent(event)


# ------------------------------------------------------------------------------
# ClustersPage: Modified to include a Remove button for regexes, counters below the craft button,
# and a Crafted Jewels grid that updates via a signal to ensure thread-safe UI updates.
class ClustersPage(QWidget):
    # Signal to deliver a crafted Cluster to the UI.
    clusterCrafted = Signal(Cluster)

    def __init__(self):
        super().__init__()
        self.cluster_attempts = 0
        self.successful_crafts = 0
        self.crafted_jewels = []  # FIFO list of crafted jewel widgets
        self.max_columns = 6  # Maximum columns in the grid
        self.init_ui()
        # Connect the signal so that UI updates happen in the main thread.
        self.clusterCrafted.connect(self.handleCraftedCluster)

    def init_ui(self):
        layout = QVBoxLayout()
        header = QLabel("Clusters")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 20))
        layout.addWidget(header)

        self.regex_list = QListWidget()
        layout.addWidget(self.regex_list)

        input_layout = QHBoxLayout()
        self.cluster_regex_input = QLineEdit()
        self.cluster_regex_input.setPlaceholderText("Insert Regex")
        self.add_regex_btn = QPushButton("Add")
        self.add_regex_btn.clicked.connect(self.add_cluster_regex)
        input_layout.addWidget(self.cluster_regex_input)
        input_layout.addWidget(self.add_regex_btn)
        self.remove_regex_btn = QPushButton("Remove")
        self.remove_regex_btn.clicked.connect(self.remove_cluster_regex)
        input_layout.addWidget(self.remove_regex_btn)
        layout.addLayout(input_layout)

        self.craft_cluster_btn = QPushButton("Craft Cluster")
        self.craft_cluster_btn.clicked.connect(self.craft_cluster)
        layout.addWidget(self.craft_cluster_btn)

        # Labels for counters.
        self.attempts_label = QLabel("Craft Attempts: 0")
        self.attempts_label.setAlignment(Qt.AlignCenter)
        self.success_label = QLabel("Successful Crafts: 0")
        self.success_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.attempts_label)
        layout.addWidget(self.success_label)

        # Crafted Jewels grid section.
        crafted_section_label = QLabel("Crafted Jewels")
        crafted_section_label.setAlignment(Qt.AlignCenter)
        crafted_section_label.setFont(QFont("Arial", 16))
        layout.addWidget(crafted_section_label)
        self.crafted_grid = QGridLayout()
        self.crafted_container = QWidget()
        self.crafted_container.setLayout(self.crafted_grid)
        layout.addWidget(self.crafted_container)

        layout.addStretch()
        self.setLayout(layout)

    def add_cluster_regex(self):
        text = self.cluster_regex_input.text().strip()
        if text:
            item = QListWidgetItem(text)
            self.regex_list.addItem(item)
            self.cluster_regex_input.clear()

    def remove_cluster_regex(self):
        for item in self.regex_list.selectedItems():
            self.regex_list.takeItem(self.regex_list.row(item))

    def addCraftedJewel(self, cluster: Cluster):
        widget = CraftedJewelWidget(cluster)
        self.crafted_jewels.append(widget)
        max_jewels = 30  # Maximum history length; adjust as needed.
        if len(self.crafted_jewels) > max_jewels:
            oldest = self.crafted_jewels.pop(0)
            oldest.setParent(None)
        self.updateCraftedGrid()

    def updateCraftedGrid(self):
        # Clear the grid and repopulate.
        while self.crafted_grid.count():
            child = self.crafted_grid.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        for index, widget in enumerate(self.crafted_jewels):
            row = index // self.max_columns
            col = index % self.max_columns
            self.crafted_grid.addWidget(widget, row, col)

    def handleCraftedCluster(self, cluster: Cluster):
        self.successful_crafts += 1
        self.success_label.setText(f"Successful Crafts: {self.successful_crafts}")
        self.addCraftedJewel(cluster)

    def craft_cluster(self):
        regexes = [
            self.regex_list.item(i).text() for i in range(self.regex_list.count())
        ]

        def attempt_callback():
            self.cluster_attempts += 1
            self.attempts_label.setText(f"Craft Attempts: {self.cluster_attempts}")

        def success_callback(cluster: Cluster):
            # Emit the signal to update UI in the main thread.
            self.clusterCrafted.emit(cluster)

        threading.Thread(
            target=lambda: cluster_module.craft_cluster(
                regexes, attempt_callback, success_callback
            ),
            daemon=True,
        ).start()


# ------------------------------------------------------------------------------
# MapsPage remains largely the same.
class MapsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QLabel("Map Crafting")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 20))
        layout.addWidget(header)

        stats_layout = QHBoxLayout()
        self.quant_spin = QSpinBox()
        self.quant_spin.setPrefix("Quant: ")
        self.quant_spin.setMaximum(1000)
        stats_layout.addWidget(self.quant_spin)

        self.rarity_spin = QSpinBox()
        self.rarity_spin.setPrefix("Rarity: ")
        self.rarity_spin.setMaximum(1000)
        stats_layout.addWidget(self.rarity_spin)

        self.packsize_spin = QSpinBox()
        self.packsize_spin.setPrefix("Pack Size: ")
        self.packsize_spin.setMaximum(1000)
        stats_layout.addWidget(self.packsize_spin)

        self.moremaps_spin = QSpinBox()
        self.moremaps_spin.setPrefix("More Maps: ")
        self.moremaps_spin.setMaximum(1000)
        stats_layout.addWidget(self.moremaps_spin)

        self.morescarabs_spin = QSpinBox()
        self.morescarabs_spin.setPrefix("More Scarabs: ")
        self.morescarabs_spin.setMaximum(1000)
        stats_layout.addWidget(self.morescarabs_spin)

        self.morecurrency_spin = QSpinBox()
        self.morecurrency_spin.setPrefix("More Currency: ")
        self.morecurrency_spin.setMaximum(1000)
        stats_layout.addWidget(self.morecurrency_spin)

        layout.addLayout(stats_layout)

        self.map_pos_label = QLabel("Map Position: Not Yet Selected")
        layout.addWidget(self.map_pos_label)

        self.map_regex_list = QListWidget()
        layout.addWidget(self.map_regex_list)

        input_layout = QHBoxLayout()
        self.map_regex_input = QLineEdit()
        self.map_regex_input.setPlaceholderText("Insert Regex")
        self.add_map_regex_btn = QPushButton("Add")
        self.add_map_regex_btn.clicked.connect(self.add_map_regex)
        input_layout.addWidget(self.map_regex_input)
        input_layout.addWidget(self.add_map_regex_btn)
        layout.addLayout(input_layout)

        buttons_layout = QHBoxLayout()
        self.craft_map_btn = QPushButton("Craft Map")
        self.craft_map_btn.clicked.connect(self.craft_map)
        buttons_layout.addWidget(self.craft_map_btn)

        self.select_map_btn = QPushButton("Select Map")
        self.select_map_btn.clicked.connect(self.select_map)
        buttons_layout.addWidget(self.select_map_btn)

        self.load_map_btn = QPushButton("Load Map Config")
        self.load_map_btn.clicked.connect(self.load_map_config)
        buttons_layout.addWidget(self.load_map_btn)

        self.save_map_btn = QPushButton("Save Map Config")
        self.save_map_btn.clicked.connect(self.save_map_config)
        buttons_layout.addWidget(self.save_map_btn)

        layout.addLayout(buttons_layout)

        self.regex_count_spin = QSpinBox()
        self.regex_count_spin.setPrefix("Regex Count: ")
        self.regex_count_spin.setMaximum(100)
        layout.addWidget(self.regex_count_spin)

        layout.addStretch()
        self.setLayout(layout)

    def add_map_regex(self):
        text = self.map_regex_input.text().strip()
        if text:
            item = QListWidgetItem(text)
            self.map_regex_list.addItem(item)
            self.map_regex_input.clear()

    def craft_map(self):
        regexes = [
            self.map_regex_list.item(i).text()
            for i in range(self.map_regex_list.count())
        ]
        regex_count = self.regex_count_spin.value()
        expected_implicits = {
            "Item Quantity": self.quant_spin.value(),
            "Item Rarity": self.rarity_spin.value(),
            "Monster Pack Size": self.packsize_spin.value(),
            "More Maps": self.moremaps_spin.value(),
            "More Scarabs": self.morescarabs_spin.value(),
            "More Currency": self.morecurrency_spin.value(),
        }
        threading.Thread(
            target=lambda: map_module.craft_map(
                regexes, regex_count, expected_implicits
            ),
            daemon=True,
        ).start()

    def select_map(self):
        def task():
            pos = bot_controller.Bot.select_pos("map-item")
            if pos:
                self.map_pos_label.setText(f"Map Position: ({pos.x}, {pos.y})")

        threading.Thread(target=task, daemon=True).start()

    def load_map_config(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Map Config", "", "JSON Files (*.json)"
        )
        if filename:
            try:
                with open(filename, "r") as f:
                    settings = json.load(f)
                self.quant_spin.setValue(int(settings.get("quant", 0)))
                self.rarity_spin.setValue(int(settings.get("rarity", 0)))
                self.packsize_spin.setValue(int(settings.get("packsize", 0)))
                self.moremaps_spin.setValue(int(settings.get("moreMaps", 0)))
                self.morescarabs_spin.setValue(int(settings.get("moreScarabs", 0)))
                self.morecurrency_spin.setValue(int(settings.get("moreCurrency", 0)))
                self.map_regex_list.clear()
                for regex in settings.get("regexes", []):
                    self.map_regex_list.addItem(QListWidgetItem(regex))
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load config: {e}")

    def save_map_config(self):
        settings = {
            "quant": self.quant_spin.value(),
            "rarity": self.rarity_spin.value(),
            "packsize": self.packsize_spin.value(),
            "moreMaps": self.moremaps_spin.value(),
            "moreScarabs": self.morescarabs_spin.value(),
            "moreCurrency": self.morecurrency_spin.value(),
            "regexes": [
                self.map_regex_list.item(i).text()
                for i in range(self.map_regex_list.count())
            ],
        }
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Map Config", "mapSettings.json", "JSON Files (*.json)"
        )
        if filename:
            try:
                with open(filename, "w") as f:
                    json.dump(settings, f, indent=2)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save config: {e}")


# ------------------------------------------------------------------------------
# ItemsPage: New section groups the "Match Any Mod" checkbox and position labels.
class ItemsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = QLabel("Item Crafting")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 20))
        layout.addWidget(header)

        self.section_container = QWidget()
        self.section_container.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        section_layout = QVBoxLayout()
        section_layout.setContentsMargins(4, 4, 4, 4)
        top_layout = QHBoxLayout()
        self.match_any_checkbox = QCheckBox("Match Any Mod")
        top_layout.addWidget(self.match_any_checkbox)
        pos_layout = QVBoxLayout()
        self.method_pos_label = QLabel("Crafting Method Position: Not Yet Selected")
        self.item_pos_label = QLabel("Item Position: Not Yet Selected")
        pos_layout.addWidget(self.method_pos_label)
        pos_layout.addWidget(self.item_pos_label)
        top_layout.addLayout(pos_layout)
        section_layout.addLayout(top_layout)
        self.section_container.setLayout(section_layout)
        self.section_container.setStyleSheet(get_section_style("Dark Purple"))
        layout.addWidget(self.section_container)

        self.item_regex_list = QListWidget()
        layout.addWidget(self.item_regex_list)

        input_layout = QHBoxLayout()
        self.item_regex_input = QLineEdit()
        self.item_regex_input.setPlaceholderText("Insert Regex")
        self.add_item_regex_btn = QPushButton("Add")
        self.add_item_regex_btn.clicked.connect(self.add_item_regex)
        input_layout.addWidget(self.item_regex_input)
        input_layout.addWidget(self.add_item_regex_btn)
        layout.addLayout(input_layout)

        buttons_layout = QHBoxLayout()
        self.craft_item_btn = QPushButton("Craft Item")
        self.craft_item_btn.clicked.connect(self.craft_item)
        buttons_layout.addWidget(self.craft_item_btn)
        self.select_method_btn = QPushButton("Select Method")
        self.select_method_btn.clicked.connect(self.select_method)
        buttons_layout.addWidget(self.select_method_btn)
        self.select_item_btn = QPushButton("Select Item")
        self.select_item_btn.clicked.connect(self.select_item)
        buttons_layout.addWidget(self.select_item_btn)
        self.load_item_btn = QPushButton("Load Regex Config")
        self.load_item_btn.clicked.connect(self.load_item_config)
        buttons_layout.addWidget(self.load_item_btn)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        self.setLayout(layout)

    def update_theme(self, new_theme):
        new_style = get_section_style(new_theme)
        self.section_container.setStyleSheet(new_style)

    def add_item_regex(self):
        text = self.item_regex_input.text().strip()
        if text:
            self.item_regex_list.addItem(QListWidgetItem(text))
            self.item_regex_input.clear()

    def craft_item(self):
        regexes = [
            self.item_regex_list.item(i).text()
            for i in range(self.item_regex_list.count())
        ]
        match_any = self.match_any_checkbox.isChecked()
        threading.Thread(
            target=lambda: item_craft_module.craft_item(regexes, match_any), daemon=True
        ).start()

    def select_method(self):
        def task():
            pos = bot_controller.Bot.select_pos("craft-method")
            if pos:
                self.method_pos_label.setText(
                    f"Crafting Method Position: ({pos.x}, {pos.y})"
                )

        threading.Thread(target=task, daemon=True).start()

    def select_item(self):
        def task():
            pos = bot_controller.Bot.select_pos("craft-item")
            if pos:
                self.item_pos_label.setText(f"Item Position: ({pos.x}, {pos.y})")

        threading.Thread(target=task, daemon=True).start()

    def load_item_config(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Regex Config", "", "Text Files (*.txt)"
        )
        if filename:
            try:
                with open(filename, "r") as f:
                    lines = f.read().splitlines()
                self.item_regex_list.clear()
                for line in lines:
                    if line.strip():
                        self.item_regex_list.addItem(QListWidgetItem(line.strip()))
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load regex config: {e}")


# ------------------------------------------------------------------------------
# MainWindow.
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Odin - PySide6 Version")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()
        self.killswitch_monitor = KillswitchMonitor()
        self.killswitch_monitor.killswitch_toggled.connect(self.update_killswitch_label)
        self.load_positions()

    def init_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout()

        sidebar = QFrame()
        sidebar.setFrameShape(QFrame.StyledPanel)
        sidebar_layout = QVBoxLayout()

        self.home_btn = QPushButton("Home")
        self.clusters_btn = QPushButton("Clusters")
        self.maps_btn = QPushButton("Maps")
        self.items_btn = QPushButton("Items")
        self.settings_btn = QPushButton("Settings")

        self.home_btn.clicked.connect(lambda: self.switch_page(0))
        self.clusters_btn.clicked.connect(lambda: self.switch_page(1))
        self.maps_btn.clicked.connect(lambda: self.switch_page(2))
        self.items_btn.clicked.connect(lambda: self.switch_page(3))
        self.settings_btn.clicked.connect(lambda: self.switch_page(4))

        sidebar_layout.addWidget(self.home_btn)
        sidebar_layout.addWidget(self.clusters_btn)
        sidebar_layout.addWidget(self.maps_btn)
        sidebar_layout.addWidget(self.items_btn)
        sidebar_layout.addWidget(self.settings_btn)

        self.killswitch_label = QLabel("Killswitch: OFF")
        sidebar_layout.addWidget(self.killswitch_label)

        sidebar_layout.addStretch()
        sidebar.setLayout(sidebar_layout)

        self.pages = QStackedWidget()
        self.calibration_page = CalibrationPage()
        self.clusters_page = ClustersPage()
        self.maps_page = MapsPage()
        self.items_page = ItemsPage()
        self.settings_page = SettingsPage()
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

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)

    def update_killswitch_label(self, state):
        self.killswitch_label.setText("Killswitch: ON" if state else "Killswitch: OFF")

    def on_theme_changed(self, theme_name):
        self.calibration_page.update_theme(theme_name)
        self.items_page.update_theme(theme_name)

    def load_positions(self):
        cluster_pos = config.get_value("cluster", "button-location")
        if cluster_pos:
            self.settings_page.cluster_calib_status.setText(
                f"({cluster_pos['x']}, {cluster_pos['y']})"
            )
        for currency in self.calibration_page.currency_labels.keys():
            pos = config.get_value("currency", currency)
            if pos:
                self.calibration_page.currency_labels[currency].setText(
                    f"({pos['x']}, {pos['y']})"
                )


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(get_stylesheet("Dark Purple"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
