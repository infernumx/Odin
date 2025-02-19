from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSpinBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import threading, json
import map_module, bot_controller
from theme import ShadowHeaderLabel


class MapsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = ShadowHeaderLabel("Map Crafting")
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
            self.map_regex_list.addItem(text)
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
                    self.map_regex_list.addItem(regex)
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

    def update_theme(self, new_theme):
        # Update the style of the section container (or any other elements)
        from theme import (
            get_section_style,
        )  # assuming you centralized theming in theme.py

        self.section_container.setStyleSheet(get_section_style(new_theme))
        # Optionally, update other widget styles if needed
