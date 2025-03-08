import json
import threading
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QPushButton,
    QLabel,
    QComboBox,
    QCheckBox,
    QSpinBox,
    QLineEdit,
    QGroupBox,
    QGridLayout,
    QFrame,
    QFileDialog,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon, QFont
from item_craft_module import CraftingStep, craft_item_advanced


class StepWidget(QWidget):
    insertAbove = Signal(QWidget)
    insertBelow = Signal(QWidget)
    removeStep = Signal(QWidget)

    def __init__(self, currencies, parent=None):
        super().__init__(parent)
        self.setObjectName("stepWidget")
        self.currencies = currencies
        self.build_ui()
        self.setStyleSheet(
            """
            QWidget#stepWidget {
                background-color: #4f009d;
                border: 2px solid #7d003f;
                border-radius: 2px;
                padding: 8px;
            }
        """
        )
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(Qt.black)
        self.setGraphicsEffect(shadow)

    def build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Left layout
        left_layout = QVBoxLayout()
        left_layout.setSpacing(8)

        # Method (Orb) Selection
        method_layout = QHBoxLayout()
        method_label = QLabel("Choose a method:")
        self.method_combo = QComboBox()
        for key, (display_name, icon_path) in self.currencies.items():
            self.method_combo.addItem(QIcon(icon_path), display_name, key)
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.method_combo)
        left_layout.addLayout(method_layout)

        # Conditions
        cond_group = QGroupBox("Conditions")
        cond_layout = QVBoxLayout()
        self.auto_success_cb = QCheckBox("Automatic success")
        cond_layout.addWidget(self.auto_success_cb)
        self.condition_input = QLineEdit()
        self.condition_input.setPlaceholderText("Condition or mod regex")
        cond_layout.addWidget(self.condition_input)
        self.logic_combo = QComboBox()
        self.logic_combo.addItems(["AND", "OR", "NOT"])
        cond_layout.addWidget(self.logic_combo)
        add_group_btn = QPushButton("Add Condition Group")
        cond_layout.addWidget(add_group_btn)
        cond_group.setLayout(cond_layout)
        left_layout.addWidget(cond_group)

        # Actions
        actions_group = QGroupBox("Actions")
        actions_layout = QGridLayout()

        # On Success
        success_label = QLabel("On Success:")
        self.success_continue_cb = QCheckBox("Continue")
        self.success_continue_cb.setChecked(True)
        self.success_gostep_cb = QCheckBox("Go to step #")
        self.success_step_spin = QSpinBox()
        self.success_step_spin.setRange(1, 999)
        self.success_step_spin.setEnabled(False)
        self.success_gostep_cb.toggled.connect(self.success_step_spin.setEnabled)

        actions_layout.addWidget(success_label, 0, 0)
        actions_layout.addWidget(self.success_continue_cb, 0, 1)
        actions_layout.addWidget(self.success_gostep_cb, 0, 2)
        actions_layout.addWidget(self.success_step_spin, 0, 3)

        # On Failure
        failure_label = QLabel("On Failure:")
        self.failure_loop_cb = QCheckBox("Loop")
        self.failure_loop_cb.setChecked(True)
        self.failure_restart_cb = QCheckBox("Restart")
        self.failure_gostep_cb = QCheckBox("Go to step #")
        self.failure_step_spin = QSpinBox()
        self.failure_step_spin.setRange(1, 999)
        self.failure_step_spin.setEnabled(False)
        self.failure_gostep_cb.toggled.connect(self.failure_step_spin.setEnabled)

        actions_layout.addWidget(failure_label, 1, 0)
        actions_layout.addWidget(self.failure_loop_cb, 1, 1)
        actions_layout.addWidget(self.failure_restart_cb, 1, 2)
        actions_layout.addWidget(self.failure_gostep_cb, 1, 3)
        actions_layout.addWidget(self.failure_step_spin, 1, 4)

        actions_group.setLayout(actions_layout)
        left_layout.addWidget(actions_group)
        main_layout.addLayout(left_layout)

        # Right layout (centered buttons)
        right_layout = QVBoxLayout()
        right_layout.addStretch()
        insert_above_btn = QPushButton("+")
        remove_btn = QPushButton("X")
        insert_below_btn = QPushButton("+")
        right_layout.addWidget(insert_above_btn, alignment=Qt.AlignCenter)
        right_layout.addWidget(remove_btn, alignment=Qt.AlignCenter)
        right_layout.addWidget(insert_below_btn, alignment=Qt.AlignCenter)
        right_layout.addStretch()
        insert_above_btn.clicked.connect(lambda: self.insertAbove.emit(self))
        remove_btn.clicked.connect(lambda: self.removeStep.emit(self))
        insert_below_btn.clicked.connect(lambda: self.insertBelow.emit(self))
        main_layout.addLayout(right_layout)

        outer_layout.addLayout(main_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setLineWidth(3)
        separator.setStyleSheet("background-color: #444444;")
        outer_layout.addWidget(separator)

    def build_crafting_step(self, index_in_sequence, total_steps):
        if self.success_gostep_cb.isChecked():
            on_success = self.success_step_spin.value() - 1
        elif self.success_continue_cb.isChecked():
            on_success = (
                index_in_sequence + 1
                if (index_in_sequence + 1) < total_steps
                else total_steps
            )
        else:
            on_success = index_in_sequence + 1

        if self.failure_gostep_cb.isChecked():
            on_failure = self.failure_step_spin.value() - 1
        elif self.failure_restart_cb.isChecked():
            on_failure = 0
        elif self.failure_loop_cb.isChecked():
            on_failure = index_in_sequence
        else:
            on_failure = -1

        return CraftingStep(
            condition_regex=self.condition_input.text().strip(),
            currency=self.method_combo.currentData(),
            on_failure=on_failure,
            on_success=on_success,
            auto_success=self.auto_success_cb.isChecked(),
            max_attempts=10,
        )

    def get_blueprint_config(self):
        return {
            "method": self.method_combo.currentData(),
            "condition": self.condition_input.text(),
            "logic": self.logic_combo.currentText(),
            "auto_success": self.auto_success_cb.isChecked(),
            "success_continue": self.success_continue_cb.isChecked(),
            "success_gostep": self.success_gostep_cb.isChecked(),
            "success_step": self.success_step_spin.value(),
            "failure_loop": self.failure_loop_cb.isChecked(),
            "failure_restart": self.failure_restart_cb.isChecked(),
            "failure_gostep": self.failure_gostep_cb.isChecked(),
            "failure_step": self.failure_step_spin.value(),
            "max_attempts": 10,
        }

    def set_blueprint_config(self, config):
        idx = self.method_combo.findData(config.get("method", ""))
        if idx >= 0:
            self.method_combo.setCurrentIndex(idx)
        self.condition_input.setText(config.get("condition", ""))
        logic = config.get("logic", "AND")
        idx_logic = self.logic_combo.findText(logic)
        if idx_logic >= 0:
            self.logic_combo.setCurrentIndex(idx_logic)
        self.auto_success_cb.setChecked(config.get("auto_success", False))
        self.success_continue_cb.setChecked(config.get("success_continue", True))
        self.success_gostep_cb.setChecked(config.get("success_gostep", False))
        self.success_step_spin.setValue(config.get("success_step", 1))
        self.failure_loop_cb.setChecked(config.get("failure_loop", True))
        self.failure_restart_cb.setChecked(config.get("failure_restart", False))
        self.failure_gostep_cb.setChecked(config.get("failure_gostep", False))
        self.failure_step_spin.setValue(config.get("failure_step", 1))


class ItemsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.currencies = {
            "chaos": ("Chaos Orb", "images/chaos.png"),
            "exalted": ("Exalted Orb", "images/exalted.png"),
            "ancient": ("Ancient Orb", "images/ancient.png"),
            "transmutation": ("Orb of Transmutation", "images/transmutation.png"),
            "augment": ("Orb of Augmentation", "images/augment.png"),
            "alteration": ("Orb of Alteration", "images/alteration.png"),
            "alchemy": ("Orb of Alchemy", "images/alchemy.png"),
            "regal": ("Regal Orb", "images/regal.png"),
            "scouring": ("Orb of Scouring", "images/scouring.png"),
            "vaal": ("Vaal Orb", "images/vaal.png"),
            "blessed": ("Blessed Orb", "images/blessed.png"),
            "cartographer": ("Cartographer's Chisel", "images/cartographer.png"),
        }
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Top controls
        top_layout = QHBoxLayout()
        start_crafting_btn = QPushButton("Start Crafting")
        start_crafting_btn.clicked.connect(self.start_crafting)
        top_layout.addWidget(start_crafting_btn)

        save_blueprint_btn = QPushButton("Save Blueprint")
        save_blueprint_btn.clicked.connect(self.save_blueprint)
        top_layout.addWidget(save_blueprint_btn)

        load_blueprint_btn = QPushButton("Load Blueprint")
        load_blueprint_btn.clicked.connect(self.load_blueprint)
        top_layout.addWidget(load_blueprint_btn)

        main_layout.addLayout(top_layout)

        header = QLabel("Item Crafting")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Roboto", 24, QFont.Bold))
        main_layout.addWidget(header)

        # Steps container
        self.steps_container = QVBoxLayout()
        self.steps_container.setSpacing(12)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.steps_container)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        add_step_btn = QPushButton("Add Step")
        add_step_btn.clicked.connect(self.add_step)
        main_layout.addWidget(add_step_btn)

        self.setLayout(main_layout)

    @Slot()
    def add_step(self):
        step_widget = StepWidget(self.currencies)
        step_widget.insertAbove.connect(self.insert_step_above)
        step_widget.insertBelow.connect(self.insert_step_below)
        step_widget.removeStep.connect(self.remove_step)
        self.steps_container.addWidget(step_widget)

    @Slot(QWidget)
    def insert_step_above(self, step_widget):
        idx = self.index_of_widget(step_widget)
        if idx >= 0:
            new_step = StepWidget(self.currencies)
            new_step.insertAbove.connect(self.insert_step_above)
            new_step.insertBelow.connect(self.insert_step_below)
            new_step.removeStep.connect(self.remove_step)
            self.steps_container.insertWidget(idx, new_step)

    @Slot(QWidget)
    def insert_step_below(self, step_widget):
        idx = self.index_of_widget(step_widget)
        if idx >= 0:
            new_step = StepWidget(self.currencies)
            new_step.insertAbove.connect(self.insert_step_above)
            new_step.insertBelow.connect(self.insert_step_below)
            new_step.removeStep.connect(self.remove_step)
            self.steps_container.insertWidget(idx + 1, new_step)

    @Slot(QWidget)
    def remove_step(self, step_widget):
        idx = self.index_of_widget(step_widget)
        if idx >= 0:
            widget = self.steps_container.itemAt(idx).widget()
            widget.setParent(None)
            widget.deleteLater()

    def index_of_widget(self, widget):
        for i in range(self.steps_container.count()):
            w = self.steps_container.itemAt(i).widget()
            if w == widget:
                return i
        return -1

    def start_crafting(self):
        steps = []
        total = self.steps_container.count()
        for i in range(total):
            widget = self.steps_container.itemAt(i).widget()
            if isinstance(widget, StepWidget):
                step = widget.build_crafting_step(i, total)
                steps.append(step)
        if not steps:
            return
        t = threading.Thread(target=lambda: craft_item_advanced(steps), daemon=True)
        t.start()

    def save_blueprint(self):
        blueprint = []
        total = self.steps_container.count()
        for i in range(total):
            widget = self.steps_container.itemAt(i).widget()
            if isinstance(widget, StepWidget):
                blueprint.append(widget.get_blueprint_config())
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Blueprint", "", "Blueprint Files (*.json)"
        )
        if filename:
            with open(filename, "w") as f:
                json.dump(blueprint, f, indent=4)

    def load_blueprint(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Blueprint", "", "Blueprint Files (*.json)"
        )
        if filename:
            with open(filename, "r") as f:
                blueprint = json.load(f)
            # Clear existing steps
            while self.steps_container.count():
                widget = self.steps_container.takeAt(0).widget()
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()
            # Load steps from blueprint
            for config in blueprint:
                step_widget = StepWidget(self.currencies)
                step_widget.set_blueprint_config(config)
                step_widget.insertAbove.connect(self.insert_step_above)
                step_widget.insertBelow.connect(self.insert_step_below)
                step_widget.removeStep.connect(self.remove_step)
                self.steps_container.addWidget(step_widget)
