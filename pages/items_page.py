from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QListWidget,
    QLineEdit,
    QPushButton,
    QLabel,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import threading
import item_craft_module
import bot_controller
from theme import ShadowHeaderLabel


class ItemsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        header = ShadowHeaderLabel("Item Crafting")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 20))
        layout.addWidget(header)

        self.section_container = QWidget()
        self.section_container.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )
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
        self.section_container.setStyleSheet(
            "background-color: #2e003e; border: 2px solid #5e085e; border-radius: 8px; padding: 4px;"
        )
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

    def add_item_regex(self):
        text = self.item_regex_input.text().strip()
        if text:
            self.item_regex_list.addItem(text)
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
        from PySide6.QtWidgets import QFileDialog, QMessageBox

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
                        self.item_regex_list.addItem(line.strip())
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load regex config: {e}")

    def update_theme(self, new_theme):
        # Update the style of the section container (or any other elements)
        from theme import (
            get_section_style,
        )  # assuming you centralized theming in theme.py

        self.section_container.setStyleSheet(get_section_style(new_theme))
        # Optionally, update other widget styles if needed
