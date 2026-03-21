from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
import os


class SelectedFilesBar(QWidget):
    file_deselected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.file_buttons = {}

        self.bar_layout = QHBoxLayout()
        self.bar_layout.setContentsMargins(12, 6, 12, 6)
        self.bar_layout.setSpacing(8)

        self.label = QLabel("Selected:")
        self.label.setObjectName("selectedLabel")
        self.bar_layout.addWidget(self.label)
        self.bar_layout.addStretch()

        self.setLayout(self.bar_layout)
        self.setObjectName("selectedFilesBar")
        self.hide()

    def update_selected_files(self, file_paths):
        for fp, btn in self.file_buttons.items():
            self.bar_layout.removeWidget(btn)
            btn.deleteLater()
        self.file_buttons.clear()

        if not file_paths:
            self.hide()
            return

        for file_path in file_paths:
            name = os.path.basename(file_path)
            display = (name[:18] + "…") if len(name) > 20 else name
            btn = QPushButton(f"📄 {display}  ✕")
            btn.setObjectName("selectedFileChip")
            btn.setToolTip(file_path)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, fp=file_path: self.file_deselected.emit(fp))
            self.file_buttons[file_path] = btn
            self.bar_layout.insertWidget(self.bar_layout.count() - 1, btn)

        self.show()
