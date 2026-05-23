"""
DeskTime benzeri Windows masaüstü ajanı.

Kurulum:
  pip install -r requirements.txt
  set AGENT_API_KEY=...
  set AGENT_USER_ID=...
  set EXCHANGE_USER=kullanici@sirket.com
  set EXCHANGE_PASSWORD=...
  python main.py

PyInstaller ile paketleme:
  pyinstaller --onefile --windowed --name aktivite-ajan main.py
"""

import sys
import time
import signal
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from pynput import keyboard, mouse

import config
from tracker.window import get_active_window
from tracker.exchange import fetch_email_stats
from tracker.files import FileMonitor
from storage.offline import OfflineStorage
from sync.client import send_activity_batch, send_email_stats, send_file_event

# ── Idle tespiti ──────────────────────────────────────────────
_last_activity = datetime.now()

def _reset_idle(*_):
    global _last_activity
    _last_activity = datetime.now()

def _is_idle() -> bool:
    return (datetime.now() - _last_activity).seconds > config.IDLE_THRESHOLD_SEC

# ── Pencere örnekleme tamponu ──────────────────────────────────
_buffer: list[dict] = []

def _collect():
    window = get_active_window()
    _buffer.append({
        "timestamp":    datetime.utcnow().isoformat(),
        "app_name":     window["process"] if window else None,
        "window_title": window["title"]   if window else None,
        "is_idle":      _is_idle(),
    })

# ── n8n'e gönderim ────────────────────────────────────────────
_storage = OfflineStorage(config.OFFLINE_DB_PATH, config.ENCRYPTION_KEY)

def _sync_activity():
    batch = list(_buffer)
    _buffer.clear()
    if not batch:
        return
    if not send_activity_batch(batch):
        for evt in batch:
            _storage.push(evt)
    else:
        _flush_offline()

def _flush_offline():
    pending = _storage.pop_all()
    if not pending:
        return
    ids, events = zip(*pending)
    if send_activity_batch(list(events)):
        _storage.delete(list(ids))

def _sync_email():
    stats = fetch_email_stats()
    send_email_stats(stats)

# ── Dosya olayı callback ──────────────────────────────────────
def _on_file_event(file_path: str, event_type: str):
    import psutil
    app = ""
    try:
        for proc in psutil.process_iter(["name", "open_files"]):
            if proc.info["open_files"]:
                paths = [f.path for f in proc.info["open_files"]]
                if file_path in paths:
                    app = proc.info["name"]
                    break
    except Exception:
        pass
    send_file_event(file_path, event_type, app)

# ── Ana giriş ────────────────────────────────────────────────
def main():
    # Klavye/fare dinleyicileri
    kb = keyboard.Listener(on_press=_reset_idle)
    ms = mouse.Listener(on_move=_reset_idle, on_click=_reset_idle, on_scroll=_reset_idle)
    kb.start()
    ms.start()

    # Dosya izleyici — kullanıcı profil ve ortak dizinleri
    watch_dirs = ["C:\\Users", "C:\\Projeler", "D:\\"]
    file_mon = FileMonitor(watch_dirs, _on_file_event)
    file_mon.start()

    # Zamanlayıcılar
    scheduler = BackgroundScheduler()
    scheduler.add_job(_collect,       "interval", seconds=config.COLLECT_INTERVAL)
    scheduler.add_job(_sync_activity, "interval", seconds=config.SYNC_INTERVAL)
    scheduler.add_job(_sync_email,    "interval", seconds=config.EXCHANGE_INTERVAL)
    scheduler.start()

    print(f"[Ajan] Başlatıldı — user_id={config.USER_ID}")

    def _stop(sig, frame):
        print("[Ajan] Durduruluyor...")
        scheduler.shutdown(wait=False)
        file_mon.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
