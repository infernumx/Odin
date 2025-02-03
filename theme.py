from PySide6.QtWidgets import QComboBox, QLineEdit, QSpinBox, QPushButton, QLabel


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


def get_section_style(theme_name: str) -> str:
    """
    Returns a stylesheet string for section containers (or similar UI elements)
    based on the provided theme name. This function uses the same theme names
    as get_stylesheet() and applies corresponding background and border colors.
    """
    if theme_name == "Dark Purple":
        background_color = "#2e003e"
        border_color = "#5e085e"  # Darker purple border
    elif theme_name == "Dark Amber":
        background_color = "#3e2c1d"
        border_color = "#ffbf00"
    elif theme_name == "Classic Dark":
        background_color = "#222222"
        border_color = "#444444"
    else:
        background_color = "#2c2c2c"
        border_color = "#555555"

    return f"background-color: {background_color}; border: 2px solid {border_color}; border-radius: 8px; padding: 4px;"


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
    elif theme_name == "Dark Amber":
        return """
            QPushButton {
                background-color: #ffbf00;
                color: black;
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0ac00;
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
