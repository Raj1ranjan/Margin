from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt as QtNS


class EmptyState(QWidget):
    """Animated empty state shown when no PDF is loaded."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 0.0
        self.setObjectName("emptyState")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)
        self.setLayout(layout)

        icon = QLabel("📄")
        icon.setObjectName("emptyIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Drop a PDF here")
        title.setObjectName("emptyTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel('or click <b>Import PDFs</b>')
        subtitle.setObjectName("emptySubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        divider = QLabel("Try these commands:")
        divider.setObjectName("emptyDivider")
        divider.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hints_layout = QHBoxLayout()
        hints_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hints_layout.setSpacing(8)
        for text in ["extract pages 1-5", "compress high", "merge selected PDFs"]:
            chip = QLabel(text)
            chip.setObjectName("emptyHintChip")
            hints_layout.addWidget(chip)

        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)
        layout.addWidget(divider)
        layout.addLayout(hints_layout)

        # Fade-in animation
        self._anim = QPropertyAnimation(self, b"opacity")
        self._anim.setDuration(600)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        QTimer.singleShot(50, self._anim.start)

    def get_opacity(self):
        return self._opacity

    def set_opacity(self, value):
        self._opacity = value
        self.setWindowOpacity(value)
        self.update()

    opacity = pyqtProperty(float, get_opacity, set_opacity)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self._opacity)

        # Dashed border box
        pen = QPen(QColor("#30363D"))
        pen.setStyle(QtNS.PenStyle.DashLine)
        pen.setWidth(2)
        pen.setDashPattern([6, 4])
        painter.setPen(pen)
        painter.setBrush(QColor(0, 0, 0, 0))
        margin = 40
        painter.drawRoundedRect(margin, margin, self.width() - margin * 2, self.height() - margin * 2, 16, 16)

        super().paintEvent(event)
