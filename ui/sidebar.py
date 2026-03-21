from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget, QFileDialog, QLabel,
    QListWidgetItem, QMenu, QHBoxLayout, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt, QThread
from PyQt6.QtGui import QColor
import os
import shutil
import fitz
from ui.components.file_item import FileItem


class _PageCountWorker(QThread):
    done = pyqtSignal(object, int)

    def __init__(self, widget, path):
        super().__init__()
        self.widget = widget
        self.path = path

    def run(self):
        try:
            doc = fitz.open(self.path)
            n = len(doc)
            doc.close()
        except Exception:
            n = 0
        self.done.emit(self.widget, n)


class Sidebar(QWidget):
    files_loaded = pyqtSignal(list)
    result_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._page_workers = []

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Import Button
        self.import_btn = QPushButton("⊕  Import PDFs")
        self.import_btn.setObjectName("importBtn")
        self.import_btn.clicked.connect(self.open_file_dialog)

        # File List
        self.file_label = QLabel("IMPORTED FILES")
        self.file_label.setObjectName("sectionLabel")
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self._show_file_context_menu)

        # Results / Activity Feed
        self.results_label = QLabel("ACTIVITY")
        self.results_label.setObjectName("sectionLabel")
        self.results_list = QListWidget()
        self.results_list.setObjectName("activityList")
        self.results_list.itemClicked.connect(self.on_result_clicked)
        self.results_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_list.customContextMenuRequested.connect(self.show_result_context_menu)

        self.setAcceptDrops(True)

        layout.addWidget(self.import_btn)
        layout.addSpacing(4)
        layout.addWidget(self.file_label)
        layout.addWidget(self.file_list, 3)
        layout.addWidget(self.results_label)
        layout.addWidget(self.results_list, 2)

        self.setLayout(layout)
        self.setFixedWidth(260)

    def add_file_item(self, file_path):
        item = QListWidgetItem()
        file_item_widget = FileItem(file_path)
        item.setSizeHint(file_item_widget.sizeHint())
        self.file_list.addItem(item)
        self.file_list.setItemWidget(item, file_item_widget)

        worker = _PageCountWorker(file_item_widget, file_path)
        worker.done.connect(lambda w, n: w.set_page_count(n))
        worker.finished.connect(lambda: self._page_workers.remove(worker) if worker in self._page_workers else None)
        self._page_workers.append(worker)
        worker.start()

    def get_all_files(self):
        files = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            widget = self.file_list.itemWidget(item)
            if widget:
                files.append(widget.file_path)
        return files

    def open_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDFs", "", "PDF Files (*.pdf)")
        if files:
            existing = self.get_all_files()
            for f in files:
                if f not in existing:
                    self.add_file_item(f)
            self.files_loaded.emit(self.get_all_files())

    def get_selected_files(self):
        selected = []
        for item in self.file_list.selectedItems():
            widget = self.file_list.itemWidget(item)
            if widget:
                selected.append(widget.file_path)
        return selected

    def add_result(self, file_path, summary: str = ""):
        """Add an activity feed entry for a completed operation."""
        filename = os.path.basename(file_path)
        display = (filename[:28] + "…") if len(filename) > 31 else filename
        text = f"✔  {display}"
        if summary:
            text += f"\n    {summary}"

        item = QListWidgetItem(text)
        item.setToolTip(file_path)
        item.setData(Qt.ItemDataRole.UserRole, file_path)
        item.setForeground(QColor("#10B981"))
        self.results_list.addItem(item)
        self.results_list.scrollToBottom()

    def on_result_clicked(self, item):
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path:
            self.result_selected.emit(file_path)

    # ── File item right-click ─────────────────────────────────────────────
    def _show_file_context_menu(self, position):
        item = self.file_list.itemAt(position)
        if not item:
            return
        widget = self.file_list.itemWidget(item)
        if not widget:
            return
        file_path = widget.file_path

        menu = QMenu(self)
        menu.addAction("📂  Open Location", lambda: self._open_location(file_path))
        menu.addAction("🗑  Remove", lambda: self._remove_file_item(item))
        menu.exec(self.file_list.mapToGlobal(position))

    def _open_location(self, file_path):
        import subprocess
        folder = os.path.dirname(file_path)
        subprocess.Popen(["xdg-open", folder])

    def _remove_file_item(self, item):
        row = self.file_list.row(item)
        self.file_list.takeItem(row)
        self.files_loaded.emit(self.get_all_files())

    # ── Result right-click ────────────────────────────────────────────────
    def show_result_context_menu(self, position):
        item = self.results_list.itemAt(position)
        if not item:
            return
        file_path = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(self)
        menu.addAction("📋  Copy to Location…", lambda: self.copy_result_file(file_path))
        menu.addAction("📂  Open Folder", lambda: self._open_location(file_path))
        menu.addAction("📌  Copy Path", lambda: self.copy_file_path(file_path))
        menu.exec(self.results_list.mapToGlobal(position))

    def copy_result_file(self, file_path):
        if not os.path.exists(file_path):
            return
        dest = QFileDialog.getSaveFileName(self, "Save PDF", os.path.basename(file_path), "PDF Files (*.pdf)")[0]
        if dest:
            try:
                shutil.copy2(file_path, dest)
                from ui.dialogs import show_success
                show_success(self.parent(), "Saved", f"Copied to:\n{dest}")
            except Exception as e:
                from ui.dialogs import show_error
                show_error(self.parent(), "Error", str(e))

    def copy_file_path(self, file_path):
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(file_path)

    # ── Drag & Drop ───────────────────────────────────────────────────────
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        existing = self.get_all_files()
        added = False
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith('.pdf') and path not in existing:
                self.add_file_item(path)
                added = True
        if added:
            self.files_loaded.emit(self.get_all_files())
