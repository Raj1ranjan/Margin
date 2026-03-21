from PyQt6.QtWidgets import QLineEdit, QListWidget, QListWidgetItem, QApplication
from PyQt6.QtGui import QPainter, QColor, QTextCharFormat, QSyntaxHighlighter, QTextDocument
from PyQt6.QtCore import Qt, pyqtSignal


_SUGGESTIONS = [
    "extract pages 1-5",
    "extract last 3 pages",
    "extract first 5 pages",
    "extract odd pages",
    "extract even pages",
    "extract pages 1, 3, 7",
    "delete pages 3-7",
    "delete pages 1, 3, 5",
    "delete all pages after 50",
    "remove blank pages",
    "merge",
    "compress high",
    "compress medium",
    "compress low",
    "rotate all pages 90",
    "rotate page 1 clockwise",
    "convert to grayscale",
    "insert page 1 of first pdf into second pdf at page 5",
]


class CommandBar(QLineEdit):
    suggestion_accepted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ghost = ""

        self._dropdown = QListWidget(self.window() if self.window() else self)
        self._dropdown.setObjectName("suggestionDropdown")
        self._dropdown.setWindowFlags(Qt.WindowType.Popup)
        self._dropdown.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._dropdown.itemClicked.connect(self._accept_suggestion)
        self._dropdown.hide()

        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text):
        t = text.lower().strip()
        if not t:
            self._ghost = ""
            self._dropdown.hide()
            self.update()
            return

        # Ghost text: best single match
        match = next((s for s in _SUGGESTIONS if s.startswith(t)), "")
        self._ghost = match[len(text):] if match else ""
        self.update()

        # Dropdown: all prefix matches
        matches = [s for s in _SUGGESTIONS if s.startswith(t)]
        if matches:
            self._show_dropdown(matches)
        else:
            self._dropdown.hide()

    def _show_dropdown(self, matches):
        self._dropdown.clear()
        for m in matches[:6]:
            self._dropdown.addItem(QListWidgetItem(m))

        # Position below the command bar
        pos = self.mapToGlobal(self.rect().bottomLeft())
        self._dropdown.move(pos)
        self._dropdown.setFixedWidth(self.width())
        self._dropdown.setFixedHeight(min(len(matches), 6) * 32 + 8)
        self._dropdown.show()
        self._dropdown.raise_()

    def _accept_suggestion(self, item):
        self.setText(item.text())
        self._dropdown.hide()
        self._ghost = ""
        self.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab and self._ghost:
            self.setText(self.text() + self._ghost)
            self._ghost = ""
            self._dropdown.hide()
            return
        if event.key() == Qt.Key.Key_Escape:
            self._dropdown.hide()
            return
        if event.key() == Qt.Key.Key_Down and self._dropdown.isVisible():
            self._dropdown.setFocus()
            self._dropdown.setCurrentRow(0)
            return
        super().keyPressEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._ghost or not self.text():
            return
        painter = QPainter(self)
        painter.setPen(QColor("#4A5568"))
        typed_width = self.fontMetrics().horizontalAdvance(self.text())
        rect = self.contentsRect().adjusted(typed_width + 10, 0, -4, 0)
        painter.drawText(rect, Qt.AlignmentFlag.AlignVCenter, self._ghost)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        # Small delay so click on dropdown registers first
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(150, self._dropdown.hide)
