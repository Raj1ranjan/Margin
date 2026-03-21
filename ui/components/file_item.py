from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
import os


class FileItem(QWidget):
    """File list item — page count loaded lazily to avoid blocking UI thread."""

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

        filename = os.path.basename(file_path)
        display_name = (filename[:22] + "…") if len(filename) > 25 else filename

        try:
            file_size = f"{os.path.getsize(file_path) / (1024 * 1024):.2f} MB"
        except OSError:
            file_size = "? MB"

        name_label = QLabel(f"📄 {display_name}")
        name_label.setObjectName("fileItemName")
        name_label.setToolTip(filename)

        self.info_label = QLabel(f"{file_size}")
        self.info_label.setObjectName("fileItemInfo")

        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        info_layout.addWidget(name_label)
        info_layout.addWidget(self.info_label)

        layout = QHBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)
        layout.addLayout(info_layout)
        layout.addStretch()
        self.setLayout(layout)

    def set_page_count(self, count):
        """Called after construction to avoid blocking the UI thread."""
        current = self.info_label.text()
        self.info_label.setText(f"{current} · {count} pages")
