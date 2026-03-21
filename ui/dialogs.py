from PyQt6.QtWidgets import QDialog, QMessageBox, QVBoxLayout, QLabel, QProgressBar, QTextEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt


class OperationProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Processing…")
        self.setModal(True)
        self.setFixedSize(420, 130)
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        self._worker = None

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 16)

        self.label = QLabel("Processing your PDF…")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(6)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancelBtn")
        self.cancel_btn.setFixedWidth(90)
        self.cancel_btn.clicked.connect(self._on_cancel)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.cancel_btn)

        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        layout.addLayout(btn_row)
        self.setLayout(layout)

    def set_worker(self, worker):
        self._worker = worker

    def update_status(self, message):
        self.label.setText(message)

    def _on_cancel(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(2000)
        self.close()


def show_error(parent, title, message):
    """Show error dialog with helpful information"""
    QMessageBox.critical(parent, f"❌ {title}", message)


def show_success(parent, title, message):
    """Show success dialog"""
    QMessageBox.information(parent, f"✅ {title}", message)


def show_warning(parent, title, message):
    """Show warning dialog"""
    QMessageBox.warning(parent, f"⚠️ {title}", message)


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Margin Help")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()

        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
            <h2>Margin - PDF Manipulation Tool</h2>
            <h3>Extract</h3>
            <ul>
                <li><code>extract pages 1-5</code></li>
                <li><code>extract pages 1, 3, 7</code></li>
                <li><code>extract the first 5 pages</code></li>
                <li><code>extract last 2 pages</code></li>
                <li><code>extract odd pages</code> / <code>extract even pages</code></li>
                <li><code>extract pages 10 to 1</code> (reverse order)</li>
                <li><code>extract pages containing "Invoice"</code></li>
            </ul>
            <h3>Delete</h3>
            <ul>
                <li><code>delete pages 3-7</code></li>
                <li><code>remove pages 1, 3, 5</code></li>
                <li><code>delete all pages after 50</code></li>
                <li><code>remove blank pages</code></li>
            </ul>
            <h3>Merge &amp; Insert</h3>
            <ul>
                <li><code>merge</code> — combine all selected PDFs</li>
                <li><code>interleave first pdf and second pdf</code></li>
                <li><code>insert page 1 of first pdf into second pdf at page 5</code></li>
                <li><code>add page 1 of first pdf to the start of second pdf</code></li>
            </ul>
            <h3>Transform</h3>
            <ul>
                <li><code>rotate page 3 clockwise</code></li>
                <li><code>rotate all pages 180</code></li>
                <li><code>convert to grayscale</code></li>
                <li><code>compress high</code> / <code>compress low</code> / <code>optimize for web</code></li>
            </ul>
            <h3>Help</h3>
            <ul>
                <li><code>how do I merge?</code></li>
                <li><code>help with extract</code></li>
            </ul>
            <h3>Keyboard Shortcuts</h3>
            <table border="1" width="100%">
                <tr><td><b>Ctrl+O</b></td><td>Open files</td></tr>
                <tr><td><b>Ctrl+Z</b></td><td>Undo</td></tr>
                <tr><td><b>Ctrl+Enter</b></td><td>Execute command</td></tr>
                <tr><td><b>F1</b></td><td>Show this help</td></tr>
            </table>
        """)

        layout.addWidget(help_text)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.setLayout(layout)