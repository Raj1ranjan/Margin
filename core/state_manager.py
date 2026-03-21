class AppState:
    def __init__(self):
        self.imported_files = []
        self.selected_files = []
        self.current_file = None

        # Each entry: {"source": [file, ...], "result": result_path}
        self._undo_stack = []

    def push(self, source_files, result_path):
        self._undo_stack.append({"source": list(source_files), "result": result_path})
        self.current_file = result_path

    def undo(self):
        """Pop the last operation. Returns the popped entry, or None."""
        if self._undo_stack:
            entry = self._undo_stack.pop()
            # current_file goes back to the source of the previous result, or the source of this op
            if self._undo_stack:
                self.current_file = self._undo_stack[-1]["result"]
            else:
                self.current_file = entry["source"][0] if entry["source"] else None
            return entry
        return None

    def can_undo(self):
        return bool(self._undo_stack)
