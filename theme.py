from PySide6.QtWidgets import QLabel, QGraphicsDropShadowEffect
from PySide6.QtGui import QFont, QColor, QPainter
from PySide6.QtCore import Qt


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


def get_calibration_style(theme_name: str) -> str:
    themes = {
        "Dark Purple": """
            QLabel {
                background-color: #2e003e;
                border: 1px solid #5e085e;
                border-radius: 4px;
                padding: 4px;
                color: #ffffff;
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


def get_section_style(theme_name: str) -> str:
    """
    Returns a stylesheet string for section containers (or similar UI elements)
    based on the provided theme name. This function uses the same theme names
    as get_stylesheet() and applies corresponding background and border colors.
    """
    if theme_name == "Dark Purple":
        background_color = "#2e003e"
        border_color = "#5e085e"  # Darker purple border
    elif theme_name == "Classic Dark":
        background_color = "#222222"
        border_color = "#444444"
    else:
        background_color = "#2c2c2c"
        border_color = "#555555"

    return f"background-color: {background_color}; border: 1px solid {border_color}; border-radius: 4px; padding: 4px;"


def get_button_style(theme_name: str) -> str:
    if theme_name == "Dark Purple":
        return """
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
    elif theme_name == "Classic Dark":
        return """
            QPushButton {
                background-color: #444444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """
    else:
        return ""


def create_header_label(text: str, theme_name: str = "Dark Purple") -> QLabel:
    """
    Creates a styled header label with a bold, large font, drop shadow, and a 1px bottom border.
    """
    label = QLabel(text)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # Set a modern font; adjust family and size as needed.
    font = QFont("Roboto", 24, QFont.Weight.Bold)
    label.setFont(font)

    # Set a bottom border via stylesheet. (Qt supports a limited subset of CSS,
    # and border-bottom is generally supported as part of the border property.)
    label.setStyleSheet("border: 0px; border-bottom: 1px solid #ffffff;")

    # Apply a drop shadow effect.
    shadow = QGraphicsDropShadowEffect(label)
    shadow.setBlurRadius(8)  # Increase for a softer shadow.
    shadow.setColor(QColor(0, 0, 0, 200))  # A dark, semi-transparent shadow.
    shadow.setOffset(0, 3)  # Vertical offset.
    label.setGraphicsEffect(shadow)

    return label


class ShadowHeaderLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        # Set a modern bold font; adjust family and size as needed.
        font = QFont("Roboto", 24, QFont.Weight.Bold)
        self.setFont(font)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Shadow settings
        self.shadowColor = QColor(0, 0, 0, 200)  # semi-transparent black
        self.shadowOffsetX = 2
        self.shadowOffsetY = 3
        # Remove the border from the stylesheet (we'll draw it manually)
        self.setStyleSheet("")

    def paint_event(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # Draw shadow text first
        painter.setPen(self.shadowColor)
        shadow_rect = self.rect().adjusted(
            self.shadowOffsetX,
            self.shadowOffsetY,
            self.shadowOffsetX,
            self.shadowOffsetY,
        )
        painter.drawText(shadow_rect, self.alignment(), self.text())

        # Draw main text on top
        painter.setPen(self.palette().color(self.foregroundRole()))
        painter.drawText(self.rect(), self.alignment(), self.text())

        # Draw a 1px bottom border, shifted down by 2 pixels.
        painter.setPen(QColor("#ffffff"))
        # Calculate the y position for the border: 2 pixels above the widget's bottom edge.
        y_position = self.height() - 2
        painter.drawLine(0, y_position, self.width(), y_position)
