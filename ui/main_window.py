import shutil
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QFileDialog, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer

from ui.command_bar import CommandBar
from ui.sidebar import Sidebar
from ui.components.pdf_viewer import PDFViewer
from ui.components.selected_files_bar import SelectedFilesBar
from ui.components.empty_state import EmptyState
from ui.components.toast import Toast
from ui.dialogs import OperationProgressDialog, show_error, show_success, show_warning, HelpDialog
from ui.workers import PDFWorker
from core.command_parser import parse
from core.executor import execute
from core.state_manager import AppState


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Margin")
        self.setGeometry(100, 100, 1200, 800)
        self.state = AppState()

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        central.setLayout(main_layout)

        self.sidebar = Sidebar()
        self.sidebar.files_loaded.connect(self.on_files_loaded)
        self.sidebar.file_list.itemSelectionChanged.connect(self.preview_selected)
        self.sidebar.result_selected.connect(self.on_result_selected)

        self.workspace = self._build_workspace()

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.workspace)

        self.setup_shortcuts()
        self.apply_styles()

    # ── Workspace ─────────────────────────────────────────────────────────
    def _build_workspace(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 8)

        # Selected files bar
        self.selected_files_bar = SelectedFilesBar()
        self.selected_files_bar.file_deselected.connect(self.on_file_deselected)

        # Viewer / empty state stack
        viewer_frame = QFrame()
        viewer_frame.setObjectName("viewerFrame")
        viewer_layout = QVBoxLayout()
        viewer_layout.setContentsMargins(0, 0, 0, 0)
        viewer_layout.setSpacing(0)

        self.viewer_stack = QStackedWidget()
        self.empty_state = EmptyState()
        self.viewer = PDFViewer()
        self.viewer_stack.addWidget(self.empty_state)   # index 0
        self.viewer_stack.addWidget(self.viewer)         # index 1
        self.viewer_stack.setCurrentIndex(0)

        viewer_layout.addWidget(self.viewer_stack)
        viewer_frame.setLayout(viewer_layout)

        # Toast (overlaid on viewer frame, parented to workspace widget)
        self.toast = Toast(widget)

        # Hint chips strip
        hint_strip = self._build_hint_strip()

        # Command bar
        self.command_bar = CommandBar()
        self.command_bar.setObjectName("commandBar")
        self.command_bar.setPlaceholderText("Type a command…  e.g. extract pages 1-5")
        self.command_bar.setFixedHeight(44)
        self.command_bar.returnPressed.connect(self.handle_command)

        # Now-viewing bar
        self.viewing_bar = self._build_viewing_bar()

        # Bottom bar
        bottom_bar = self._build_bottom_bar()

        layout.addWidget(self.selected_files_bar)
        layout.addWidget(viewer_frame, 5)
        layout.addWidget(hint_strip)
        layout.addWidget(self.command_bar)
        layout.addWidget(self.viewing_bar)
        layout.addLayout(bottom_bar)

        widget.setLayout(layout)
        return widget

    def _build_hint_strip(self):
        strip = QWidget()
        strip.setObjectName("hintStrip")
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        label = QLabel("Quick:")
        label.setObjectName("hintLabel")
        layout.addWidget(label)

        for cmd in ["Extract Pages", "Compress", "Merge", "Delete Pages", "Rotate"]:
            chip = QPushButton(cmd)
            chip.setObjectName("hintChip")
            chip.setCursor(Qt.CursorShape.PointingHandCursor)
            # Map chip label → command text
            cmd_map = {
                "Extract Pages": "extract pages 1-5",
                "Compress": "compress high",
                "Merge": "merge",
                "Delete Pages": "delete pages ",
                "Rotate": "rotate all pages 90",
            }
            chip.clicked.connect(lambda _, c=cmd_map[cmd]: self._fill_command(c))
            layout.addWidget(chip)

        layout.addStretch()
        strip.setLayout(layout)
        return strip

    def _fill_command(self, text):
        self.command_bar.setText(text)
        self.command_bar.setFocus()
        self.command_bar.setCursorPosition(len(text))

    def _build_viewing_bar(self):
        bar = QFrame()
        bar.setObjectName("viewingBar")
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)

        self.viewing_badge = QLabel("SOURCE")
        self.viewing_badge.setObjectName("viewingBadge")
        self.viewing_name = QLabel("No file loaded")
        self.viewing_name.setObjectName("viewingName")
        self.viewing_size = QLabel("")
        self.viewing_size.setObjectName("viewingSize")

        layout.addWidget(self.viewing_badge)
        layout.addWidget(self.viewing_name)
        layout.addStretch()
        layout.addWidget(self.viewing_size)
        bar.setLayout(layout)
        return bar

    def _build_bottom_bar(self):
        layout = QHBoxLayout()

        self.undo_btn = QPushButton("↩  Undo")
        self.undo_btn.setObjectName("secondaryBtn")
        self.undo_btn.clicked.connect(self.handle_undo)

        self.clear_outputs_btn = QPushButton("🗑  Clear Outputs")
        self.clear_outputs_btn.setObjectName("dangerBtn")
        self.clear_outputs_btn.clicked.connect(self.clear_outputs)

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(self.undo_btn)
        layout.addWidget(self.clear_outputs_btn)
        layout.addWidget(self.status_label)
        layout.addStretch()
        return layout

    # ── Viewing bar helper ────────────────────────────────────────────────
    def _update_viewing_bar(self, file_path, is_result=False):
        try:
            b = os.path.getsize(file_path)
            size_str = f"{b/1024:.1f} KB" if b < 1024*1024 else f"{b/(1024*1024):.2f} MB"
        except Exception:
            size_str = ""
        self.viewing_name.setText(os.path.basename(file_path))
        self.viewing_size.setText(size_str)
        self.viewing_badge.setText("RESULT" if is_result else "SOURCE")
        self.viewing_badge.setProperty("resultBadge", is_result)
        self.viewing_badge.style().unpolish(self.viewing_badge)
        self.viewing_badge.style().polish(self.viewing_badge)

    # ── Sidebar callbacks ─────────────────────────────────────────────────
    def on_files_loaded(self, files):
        self.state.imported_files = files
        self.status_label.setText(f"Loaded {len(files)} file(s)")

    def preview_selected(self):
        selected = self.sidebar.get_selected_files()
        self.selected_files_bar.update_selected_files(selected)
        if selected:
            self.viewer.load_pdf(selected[0])
            self.viewer_stack.setCurrentIndex(1)
            self._update_viewing_bar(selected[0], is_result=False)
            self.state.current_file = selected[0]

    def on_file_deselected(self, file_path):
        for i in range(self.sidebar.file_list.count()):
            item = self.sidebar.file_list.item(i)
            widget = self.sidebar.file_list.itemWidget(item)
            if widget and widget.file_path == file_path:
                item.setSelected(False)
                break

    def on_result_selected(self, file_path):
        self.viewer.load_pdf(file_path)
        self.viewer_stack.setCurrentIndex(1)
        self._update_viewing_bar(file_path, is_result=True)
        self.status_label.setText(f"Viewing: {os.path.basename(file_path)}")

    # ── Command execution ─────────────────────────────────────────────────
    def handle_command(self):
        command = self.command_bar.text().strip()
        selected_files = self.sidebar.get_selected_files()

        if not command:
            show_warning(self, "No Command", "Please enter a command.")
            return
        if not selected_files:
            show_error(self, "No Files Selected", "Please select PDF files from the sidebar first.")
            return

        progress = OperationProgressDialog(self)
        progress.show()

        self.worker = PDFWorker(command, selected_files, self.state)
        progress.set_worker(self.worker)
        self.worker.progress.connect(progress.update_status)
        self.worker.finished.connect(lambda result, action: self._on_finished(result, action, progress))
        self.worker.error.connect(lambda err: self._on_error(err, progress))
        self.worker.start()

    def _on_finished(self, result_path, action, progress_dialog):
        progress_dialog.close()

        if result_path.startswith("__help__:"):
            show_success(self, "Help", result_path[len("__help__:"):])
            self.status_label.setText("💡 Help shown")
            self.command_bar.clear()
            return

        self.viewer.load_pdf(result_path)
        self.viewer_stack.setCurrentIndex(1)
        self._update_viewing_bar(result_path, is_result=True)

        # Build activity feed summary
        summary = self._build_summary(action, result_path)
        self.sidebar.add_result(result_path, summary)

        self.status_label.setText(f"✅ {summary}")
        self.toast.show_message(f"✔  {summary}")
        self.command_bar.clear()

    def _build_summary(self, action, result_path):
        try:
            size_kb = os.path.getsize(result_path) / 1024
            size_str = f"{size_kb:.0f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
        except Exception:
            size_str = ""

        if action == "compress":
            try:
                orig = os.path.getsize(self.sidebar.get_selected_files()[0]) / 1024
                return f"Compressed  {orig:.0f} KB → {size_str}"
            except Exception:
                return "Compressed"
        labels = {
            "extract_range": "Extracted pages",
            "extract_pages": "Extracted pages",
            "extract_parity": "Extracted pages",
            "extract_keyword": "Extracted pages",
            "delete_range": "Deleted pages",
            "delete_pages": "Deleted pages",
            "delete_blank": "Removed blank pages",
            "merge": "Merged PDFs",
            "insert_cross": "Inserted page",
            "insert_range": "Inserted pages",
            "interleave": "Interleaved PDFs",
            "rotate": "Rotated pages",
            "grayscale": "Converted to grayscale",
        }
        label = labels.get(action, "Done")
        return f"{label}  →  {os.path.basename(result_path)}"

    def _on_error(self, error_message, progress_dialog):
        progress_dialog.close()
        show_error(self, "Operation Failed", error_message)
        self.status_label.setText(f"❌ {error_message}")

    # ── Undo ──────────────────────────────────────────────────────────────
    def handle_undo(self):
        entry = self.state.undo()
        if entry:
            source = entry.get("source")
            if source:
                self.viewer.load_pdf(source[0])
                self.viewer_stack.setCurrentIndex(1)
                self._update_viewing_bar(source[0], is_result=False)
            results_list = self.sidebar.results_list
            if results_list.count() > 0:
                results_list.takeItem(results_list.count() - 1)
            self.status_label.setText("↩️ Undone")
        else:
            self.status_label.setText("Nothing to undo")

    # ── Clear outputs ─────────────────────────────────────────────────────
    def clear_outputs(self):
        import glob
        from PyQt6.QtWidgets import QMessageBox
        outputs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")
        pdf_files = glob.glob(os.path.join(outputs_dir, "*.pdf"))
        if not pdf_files:
            self.status_label.setText("No outputs to clear")
            return
        reply = QMessageBox.question(
            self, "Clear Outputs", f"Delete {len(pdf_files)} output file(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            for f in pdf_files:
                try:
                    os.remove(f)
                except Exception:
                    pass
            self.sidebar.results_list.clear()
            self.state._undo_stack.clear()
            self.viewer_stack.setCurrentIndex(0)
            self.status_label.setText(f"🗑️ Cleared {len(pdf_files)} output(s)")

    # ── Styles ────────────────────────────────────────────────────────────
    def apply_styles(self):
        try:
            with open("assets/styles/dark_theme.qss") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            self.setStyleSheet("QMainWindow { background-color: #0B0F17; color: #F0F6FC; }")

    # ── Shortcuts ─────────────────────────────────────────────────────────
    def setup_shortcuts(self):
        from PyQt6.QtGui import QKeySequence, QShortcut
        QShortcut(QKeySequence.StandardKey.Open, self).activated.connect(self.sidebar.open_file_dialog)
        QShortcut(QKeySequence.StandardKey.Undo, self).activated.connect(self.handle_undo)
        QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Return), self).activated.connect(self.handle_command)
        QShortcut(QKeySequence.StandardKey.Delete, self).activated.connect(self._delete_selected_files)
        QShortcut(QKeySequence.StandardKey.HelpContents, self).activated.connect(self._show_help)

    def _delete_selected_files(self):
        for item in self.sidebar.file_list.selectedItems():
            self.sidebar.file_list.takeItem(self.sidebar.file_list.row(item))
        all_files = self.sidebar.get_all_files()
        self.state.imported_files = all_files
        self.sidebar.files_loaded.emit(all_files)
        self.selected_files_bar.update_selected_files([])

    def _show_help(self):
        HelpDialog(self).exec()
