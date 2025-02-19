from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QGridLayout,
    QLineEdit,
    QPushButton,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import threading
import cluster_module

from .crafted_jewel_widget import CraftedJewelWidget
from mytypes import Cluster
from theme import ShadowHeaderLabel


class ClustersPage(QWidget):
    clusterCrafted = Signal(Cluster)

    def __init__(self):
        super().__init__()
        self.cluster_attempts = 0
        self.successful_crafts = 0
        self.crafted_jewels = []
        self.max_columns = 6
        self.init_ui()
        self.clusterCrafted.connect(self.handleCraftedCluster)

    def init_ui(self):
        layout = QVBoxLayout()
        header = ShadowHeaderLabel("Clusters")
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

        self.attempts_label = QLabel("Craft Attempts: 0")
        self.attempts_label.setAlignment(Qt.AlignCenter)
        self.success_label = QLabel("Successful Crafts: 0")
        self.success_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.attempts_label)
        layout.addWidget(self.success_label)

        # Crafted Jewels grid section.
        crafted_section_label = ShadowHeaderLabel("Crafted Jewels")
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
        max_jewels = 30
        if len(self.crafted_jewels) > max_jewels:
            oldest = self.crafted_jewels.pop(0)
            oldest.setParent(None)
        self.updateCraftedGrid()

    def updateCraftedGrid(self):
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
            self.clusterCrafted.emit(cluster)

        threading.Thread(
            target=lambda: cluster_module.craft_cluster(
                regexes, attempt_callback, success_callback
            ),
            daemon=True,
        ).start()

    def update_theme(self, new_theme):
        # Update the style of the section container (or any other elements)
        from theme import (
            get_section_style,
        )  # assuming you centralized theming in theme.py

        self.section_container.setStyleSheet(get_section_style(new_theme))
        # Optionally, update other widget styles if needed
