import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCHED_EXTENSIONS = {".xlsx", ".xls", ".docx", ".doc", ".pdf", ".dwg", ".nc1"}


class _FileHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self._callback = callback

    def _check(self, event, event_type):
        if event.is_directory:
            return
        import os
        _, ext = os.path.splitext(event.src_path)
        if ext.lower() in WATCHED_EXTENSIONS:
            self._callback(event.src_path, event_type)

    def on_created(self, event):
        self._check(event, "created")

    def on_modified(self, event):
        self._check(event, "modified")


class FileMonitor:
    def __init__(self, watch_paths: list, callback):
        self._observer = Observer()
        handler = _FileHandler(callback)
        for path in watch_paths:
            self._observer.schedule(handler, path, recursive=True)

    def start(self):
        self._observer.start()

    def stop(self):
        self._observer.stop()
        self._observer.join()
