from PyQt6.QtCore import QThread, pyqtSignal
from core.command_parser import parse
from core.executor import execute
from utils.logger import log_operation, log_error, log_info


class PDFWorker(QThread):
    finished = pyqtSignal(str, str)  # (result_path, action)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, command, selected_files, state):
        super().__init__()
        self.command = command
        self.selected_files = selected_files
        self.state = state
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            log_info(f"Starting operation: '{self.command}' with {len(self.selected_files)} files")
            self.progress.emit("Parsing command...")

            intent = parse(self.command, self.selected_files)

            if not intent:
                error_msg = f"Could not understand command: '{self.command}'"
                log_error("command_parsing", error_msg)
                self.error.emit(error_msg)
                return

            if self._cancelled:
                return

            self.progress.emit("Executing operation...")
            self.state.selected_files = self.selected_files

            result = execute(intent, self.state)

            if self._cancelled:
                return

            if isinstance(result, tuple) and result[0] == "help":
                self.finished.emit(f"__help__:{result[1]}", "help")
                return

            if isinstance(result, str) and result.lower().endswith('.pdf'):
                self.state.push(self.selected_files, result)
                log_operation(intent.get("action", "unknown"), f"Result: {result}")
                self.finished.emit(result, intent.get("action", "unknown"))
            else:
                log_error(intent.get("action", "unknown"), str(result))
                self.error.emit(str(result))

        except Exception as e:
            if not self._cancelled:
                error_msg = f"Operation failed: {str(e)}"
                log_error("worker_execution", error_msg, f"Command: {self.command}")
                self.error.emit(error_msg)
