from PyQt6.QtWidgets import QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont


class Toast(QLabel):
    """Slide-in toast notification anchored to a parent widget."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("toast")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(False)
        self.hide()

    def show_message(self, message: str, duration: int = 3000):
        self.setText(message)
        self.adjustSize()
        self.setFixedWidth(max(self.sizeHint().width() + 32, 260))
        self.setFixedHeight(40)

        # Position: bottom-center of parent
        parent = self.parentWidget()
        x = (parent.width() - self.width()) // 2
        y_end = parent.height() - 60
        y_start = y_end + 20

        self.move(x, y_start)
        self.show()
        self.raise_()

        self._anim_in = QPropertyAnimation(self, b"pos")
        self._anim_in.setDuration(280)
        self._anim_in.setStartValue(QPoint(x, y_start))
        self._anim_in.setEndValue(QPoint(x, y_end))
        self._anim_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_in.start()

        QTimer.singleShot(duration, self._slide_out)

    def _slide_out(self):
        parent = self.parentWidget()
        x = (parent.width() - self.width()) // 2
        y_end = self.y() + 20

        self._anim_out = QPropertyAnimation(self, b"pos")
        self._anim_out.setDuration(220)
        self._anim_out.setStartValue(self.pos())
        self._anim_out.setEndValue(QPoint(x, y_end))
        self._anim_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self._anim_out.finished.connect(self.hide)
        self._anim_out.start()
