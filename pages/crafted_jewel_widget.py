from PySide6.QtWidgets import QWidget, QStylePainter, QToolTip
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QPixmap, QCursor
from mytypes import Cluster


class CraftedJewelWidget(QWidget):
    def __init__(self, cluster: Cluster):
        super().__init__()
        self.cluster = cluster
        self.setFixedSize(39, 39)
        image_file = f"images/{cluster.jewel_type.lower().replace(' ', '_')}.png"
        self.pixmap = QPixmap(image_file).scaled(
            39, 39, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

    def paintEvent(self, event):
        painter = QStylePainter(self)
        if not self.pixmap.isNull():
            painter.drawPixmap(0, 0, self.pixmap)
        else:
            painter.drawText(self.rect(), Qt.AlignCenter, "?")

    def enterEvent(self, event):
        tooltip_text = f"<b>Item Info:</b><br>"
        tooltip_text += f"Item Level: {self.cluster.ilvl}<br>"
        tooltip_text += f"Passives: {self.cluster.passives}<br>"
        tooltip_text += f"Jewel Type: {self.cluster.jewel_type}<br><br>"
        tooltip_text += "<b>Mods:</b><br>" + "<br>".join(self.cluster.mods)
        # Show the tooltip relative to this widget.
        QToolTip.showText(QCursor.pos(), tooltip_text, self)
        super().enterEvent(event)

    def leaveEvent(self, event):
        QToolTip.hideText()
        super().leaveEvent(event)
