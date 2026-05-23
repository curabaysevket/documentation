import json
import sqlite3
import threading
from cryptography.fernet import Fernet


class OfflineStorage:
    def __init__(self, db_path: str, encryption_key: bytes | None = None):
        self._lock = threading.Lock()
        if encryption_key:
            self._fernet = Fernet(encryption_key)
        else:
            self._fernet = None
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS pending_events (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                payload BLOB    NOT NULL,
                created TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)
        self._conn.commit()

    def push(self, data: dict):
        raw = json.dumps(data).encode()
        blob = self._fernet.encrypt(raw) if self._fernet else raw
        with self._lock:
            self._conn.execute(
                "INSERT INTO pending_events (payload) VALUES (?)", (blob,)
            )
            self._conn.commit()

    def pop_all(self) -> list[tuple[int, dict]]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT id, payload FROM pending_events ORDER BY id LIMIT 200"
            ).fetchall()
        result = []
        for row_id, blob in rows:
            raw = self._fernet.decrypt(blob) if self._fernet else blob
            result.append((row_id, json.loads(raw)))
        return result

    def delete(self, ids: list[int]):
        if not ids:
            return
        placeholders = ",".join("?" * len(ids))
        with self._lock:
            self._conn.execute(
                f"DELETE FROM pending_events WHERE id IN ({placeholders})", ids
            )
            self._conn.commit()
