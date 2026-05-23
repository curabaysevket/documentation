import sys


def get_active_window():
    if sys.platform == "win32":
        return _get_windows()
    return None


def _get_windows():
    try:
        import win32gui
        import win32process
        import psutil

        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            process_name = psutil.Process(pid).name()
        except psutil.NoSuchProcess:
            process_name = "unknown"
        return {"title": title, "process": process_name, "pid": pid}
    except Exception:
        return None
