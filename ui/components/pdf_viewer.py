import fitz
from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QWidget, QScrollArea, QHBoxLayout, QPushButton, QSpinBox, QComboBox
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, pyqtSignal


class PDFViewer(QWidget):
    page_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.doc = None
        self.current_page = 0
        self.zoom_level = 1.0

        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(6)

        self.prev_btn = QPushButton("‹ Prev")
        self.prev_btn.setObjectName("navBtn")
        self.prev_btn.clicked.connect(self.previous_page)

        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.setFixedWidth(60)
        self.page_spin.valueChanged.connect(self._on_spin_changed)

        self.page_label = QLabel("of 0")

        self.next_btn = QPushButton("Next ›")
        self.next_btn.setObjectName("navBtn")
        self.next_btn.clicked.connect(self.next_page)

        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["50%", "75%", "100%", "125%", "150%", "200%"])
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.currentTextChanged.connect(self.set_zoom)

        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(QLabel("Page:"))
        nav_layout.addWidget(self.page_spin)
        nav_layout.addWidget(self.page_label)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(QLabel("Zoom:"))
        nav_layout.addWidget(self.zoom_combo)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.page_display = QLabel()
        self.page_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.page_display)

        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(nav_layout)
        layout.addWidget(self.scroll)
        self.setLayout(layout)

        self._spin_programmatic = False
        self.update_navigation_buttons()

    def load_pdf(self, path):
        # Close previous document to free file handle
        if self.doc:
            self.doc.close()
            self.doc = None
        try:
            self.doc = fitz.open(path)
            self.current_page = 0
            self._spin_programmatic = True
            self.page_spin.setMaximum(len(self.doc))
            self.page_spin.setValue(1)
            self._spin_programmatic = False
            self.render_page()
            self.update_navigation_buttons()
        except Exception as e:
            self.page_display.setText(f"Error loading PDF:\n{e}")

    def render_page(self):
        if not self.doc:
            return
        try:
            page = self.doc[self.current_page]
            mat = fitz.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=mat)
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            self.page_display.setPixmap(QPixmap.fromImage(img))
            self.page_label.setText(f"of {len(self.doc)}")
            self.page_changed.emit(self.current_page + 1)
        except Exception as e:
            self.page_display.setText(f"Error rendering page:\n{e}")

    def _on_spin_changed(self, value):
        if self._spin_programmatic:
            return
        if self.doc:
            self.current_page = max(0, min(value - 1, len(self.doc) - 1))
            self.render_page()
            self.update_navigation_buttons()

    def next_page(self):
        if self.doc and self.current_page < len(self.doc) - 1:
            self.current_page += 1
            self._spin_programmatic = True
            self.page_spin.setValue(self.current_page + 1)
            self._spin_programmatic = False
            self.render_page()
            self.update_navigation_buttons()

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._spin_programmatic = True
            self.page_spin.setValue(self.current_page + 1)
            self._spin_programmatic = False
            self.render_page()
            self.update_navigation_buttons()

    def set_zoom(self, zoom_text):
        self.zoom_level = float(zoom_text.rstrip('%')) / 100.0
        if self.doc:
            self.render_page()

    def update_navigation_buttons(self):
        has_doc = self.doc is not None
        self.prev_btn.setEnabled(has_doc and self.current_page > 0)
        self.next_btn.setEnabled(has_doc and self.current_page < (len(self.doc) - 1 if has_doc else 0))
