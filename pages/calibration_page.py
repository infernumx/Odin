from PySide6.QtWidgets import (
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QSizePolicy,
    QLabel,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QFont
import os, threading
import calibration_module
import config
from theme import ShadowHeaderLabel, get_section_style, get_calibration_style


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

        header = ShadowHeaderLabel("Calibration")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
            btn.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
            )
            container_layout.addWidget(btn)
            container_layout.addSpacing(2)
            img_path = os.path.join("images", img_file)
            img_label = QLabel()
            if os.path.exists(img_path):
                pixmap = QPixmap(img_path).scaled(
                    39,
                    39,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                img_label.setPixmap(pixmap)
                img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                img_label.setText(display_name)
            img_label.setFixedWidth(45)
            container_layout.addWidget(img_label)
            container_layout.addSpacing(2)
            status = QLabel("???")
            status.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fixed_width = status.fontMetrics().horizontalAdvance("XXXXXXXXXXXX")
            status.setFixedWidth(fixed_width)
            container_layout.addWidget(status)
            container.setLayout(container_layout)
            # Use container style from config
            # container.setStyleSheet(
            #    "background-color: #2e003e; border: 1px solid #5e085e; border-radius: 4px; padding: 4px;"
            # )
            container.setStyleSheet(get_section_style("Classic Dark"))
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
            if pos:
                status = f"({pos['x']}, {pos['y']})"
                config.set_value(pos, "currency", currency)
                label_widget.setText(status)

        threading.Thread(target=task, daemon=True).start()

    def update_theme(self, new_theme):
        # Here you can update the style; for now, we simply set a default.

        for container in self.containers:
            container.setStyleSheet(get_section_style(new_theme))
