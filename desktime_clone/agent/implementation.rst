.. _desktime-agent-implementation:

========================
Ajan Uygulama Detayları
========================

Proje Yapısı
-------------

.. code-block:: text

   agent/
   ├── core/
   │   ├── tracker.py        # Ana takip döngüsü (APScheduler)
   │   ├── window.py         # Aktif pencere/process tespiti
   │   ├── activity.py       # Klavye/fare aktivite dedektörü
   │   ├── screenshot.py     # Ekran görüntüsü alma + blur
   │   └── storage.py        # Offline SQLite buffer (şifreli)
   ├── sync/
   │   ├── api_client.py     # REST API gönderici (httpx)
   │   └── ws_client.py      # WebSocket gerçek zamanlı bağlantı
   ├── config.py             # Server URL, API key, ayarlar
   ├── main.py               # Giriş noktası
   └── requirements.txt

Aktif Pencere Tespiti
----------------------

**Windows:**

.. code-block:: python

   import win32gui
   import win32process
   import psutil

   def get_active_window_windows():
       hwnd = win32gui.GetForegroundWindow()
       title = win32gui.GetWindowText(hwnd)
       _, pid = win32process.GetWindowThreadProcessId(hwnd)
       process_name = psutil.Process(pid).name()
       return {"title": title, "process": process_name, "pid": pid}

**Linux (X11):**

.. code-block:: python

   import subprocess

   def get_active_window_linux():
       try:
           win_id = subprocess.check_output(
               ["xdotool", "getactivewindow"], text=True
           ).strip()
           title = subprocess.check_output(
               ["xdotool", "getwindowname", win_id], text=True
           ).strip()
           pid = subprocess.check_output(
               ["xdotool", "getwindowpid", win_id], text=True
           ).strip()
           process_name = subprocess.check_output(
               ["ps", "-p", pid, "-o", "comm="], text=True
           ).strip()
           return {"title": title, "process": process_name, "pid": int(pid)}
       except subprocess.CalledProcessError:
           return None

**Platform-bağımsız dispatcher:**

.. code-block:: python

   import sys

   def get_active_window():
       if sys.platform == "win32":
           return get_active_window_windows()
       else:
           return get_active_window_linux()

Aktivite (Idle) Tespiti
------------------------

.. code-block:: python

   from pynput import keyboard, mouse
   from datetime import datetime, timedelta

   IDLE_THRESHOLD_SECONDS = 300  # 5 dakika

   class ActivityMonitor:
       def __init__(self):
           self.last_activity = datetime.now()
           self._kb = keyboard.Listener(on_press=self._on_event)
           self._ms = mouse.Listener(on_move=self._on_event,
                                     on_click=self._on_event,
                                     on_scroll=self._on_event)

       def _on_event(self, *args):
           self.last_activity = datetime.now()

       def is_idle(self):
           return (datetime.now() - self.last_activity).seconds > IDLE_THRESHOLD_SECONDS

       def start(self):
           self._kb.start()
           self._ms.start()

Offline SQLite Buffer
----------------------

.. code-block:: python

   import sqlite3
   from cryptography.fernet import Fernet

   class OfflineStorage:
       def __init__(self, db_path: str, encryption_key: bytes):
           self.fernet = Fernet(encryption_key)
           self.conn = sqlite3.connect(db_path)
           self._init_schema()

       def _init_schema(self):
           self.conn.execute("""
               CREATE TABLE IF NOT EXISTS pending_events (
                   id      INTEGER PRIMARY KEY AUTOINCREMENT,
                   payload BLOB NOT NULL,     -- AES-256 şifreli JSON
                   created TEXT NOT NULL
               )
           """)
           self.conn.commit()

       def push(self, data: dict):
           import json
           encrypted = self.fernet.encrypt(json.dumps(data).encode())
           self.conn.execute(
               "INSERT INTO pending_events (payload, created) VALUES (?, datetime('now'))",
               (encrypted,)
           )
           self.conn.commit()

       def pop_all(self) -> list:
           import json
           rows = self.conn.execute(
               "SELECT id, payload FROM pending_events ORDER BY id LIMIT 100"
           ).fetchall()
           results = []
           for row_id, payload in rows:
               results.append((row_id, json.loads(self.fernet.decrypt(payload))))
           return results

       def delete(self, ids: list):
           self.conn.execute(
               f"DELETE FROM pending_events WHERE id IN ({','.join('?'*len(ids))})", ids
           )
           self.conn.commit()

Ekran Görüntüsü Alma
---------------------

.. code-block:: python

   from PIL import ImageGrab, ImageFilter
   import io

   def capture_screenshot(blur: bool = False, quality: int = 50) -> bytes:
       img = ImageGrab.grab()
       if blur:
           img = img.filter(ImageFilter.GaussianBlur(radius=10))
       buf = io.BytesIO()
       img.save(buf, format="JPEG", quality=quality)
       return buf.getvalue()

Ana Takip Döngüsü
------------------

.. code-block:: python

   from apscheduler.schedulers.background import BackgroundScheduler

   class Tracker:
       def __init__(self, config, storage, api_client, monitor):
           self.config = config
           self.storage = storage
           self.api = api_client
           self.monitor = monitor
           self.scheduler = BackgroundScheduler()

       def _collect_activity(self):
           window = get_active_window()
           event = {
               "timestamp": datetime.utcnow().isoformat(),
               "app_name": window["process"] if window else None,
               "window_title": window["title"] if window else None,
               "is_idle": self.monitor.is_idle(),
           }
           self.storage.push(event)

       def _sync_to_server(self):
           pending = self.storage.pop_all()
           if not pending:
               return
           ids, events = zip(*pending)
           if self.api.send_batch(events):
               self.storage.delete(list(ids))

       def start(self):
           self.monitor.start()
           self.scheduler.add_job(self._collect_activity, "interval", seconds=1)
           self.scheduler.add_job(self._sync_to_server, "interval", seconds=60)
           self.scheduler.start()

Paketleme
----------

**Windows (.exe):**

.. code-block:: bash

   pip install pyinstaller
   pyinstaller --onefile --windowed --name desktime-agent main.py

**Linux (AppImage):**

.. code-block:: bash

   pip install pyinstaller
   pyinstaller --onefile --name desktime-agent main.py
   # AppImage için appimage-builder kullanılır
