.. _desktime-backend-implementation:

===========================
Backend Uygulama Detayları
===========================

Proje Yapısı
-------------

.. code-block:: text

   backend/
   ├── api/
   │   ├── auth.py           # JWT kimlik doğrulama
   │   ├── ingest.py         # Ajan veri alma endpoint'leri
   │   ├── dashboard.py      # Dashboard/rapor sorguları
   │   ├── screenshots.py    # Ekran görüntüsü yönetimi
   │   ├── projects.py       # Proje & görev yönetimi
   │   ├── teams.py          # Ekip/kullanıcı yönetimi
   │   └── integrations.py   # Jira, Google Calendar köprüleri
   ├── workers/
   │   ├── productivity.py   # Celery: üretkenlik sınıflandırma
   │   └── media.py          # Celery: ekran görüntüsü blur/sıkıştırma
   ├── models/               # SQLAlchemy ORM modelleri
   │   ├── user.py
   │   ├── activity.py
   │   ├── screenshot.py
   │   └── project.py
   ├── core/
   │   ├── security.py       # JWT yardımcı fonksiyonlar
   │   ├── config.py         # Ortam değişkenleri (Pydantic Settings)
   │   └── ws_manager.py     # WebSocket bağlantı yöneticisi
   ├── db.py                 # Async SQLAlchemy + Alembic
   ├── main.py               # FastAPI app + router kayıtları
   └── requirements.txt

Uygulama Başlatma
------------------

.. code-block:: python

   # main.py
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware
   from api import auth, ingest, dashboard, screenshots, projects, teams
   from core.ws_manager import ws_router

   app = FastAPI(title="DeskTime Clone API", version="1.0.0")

   app.add_middleware(CORSMiddleware, allow_origins=["*"],
                      allow_methods=["*"], allow_headers=["*"])

   app.include_router(auth.router,        prefix="/api/v1/auth")
   app.include_router(ingest.router,      prefix="/api/v1/ingest")
   app.include_router(dashboard.router,   prefix="/api/v1/dashboard")
   app.include_router(screenshots.router, prefix="/api/v1/screenshots")
   app.include_router(projects.router,    prefix="/api/v1/projects")
   app.include_router(teams.router,       prefix="/api/v1/teams")
   app.include_router(ws_router)

Veri Alma Endpoint'i (Ingest)
------------------------------

.. code-block:: python

   # api/ingest.py
   from fastapi import APIRouter, Depends, HTTPException
   from pydantic import BaseModel
   from typing import List
   from workers.productivity import classify_batch
   from core.security import get_current_user

   router = APIRouter()

   class ActivityEvent(BaseModel):
       timestamp: str
       app_name: str | None
       window_title: str | None
       is_idle: bool
       duration_sec: int = 60

   class ActivityBatch(BaseModel):
       events: List[ActivityEvent]

   @router.post("/activity")
   async def ingest_activity(batch: ActivityBatch,
                              current_user=Depends(get_current_user)):
       # Kuyruğa gönder — Celery async işleyecek
       classify_batch.delay(
           user_id=current_user.id,
           events=[e.model_dump() for e in batch.events]
       )
       return {"accepted": len(batch.events)}

Üretkenlik Celery Worker
-------------------------

.. code-block:: python

   # workers/productivity.py
   from celery import shared_task
   from db import get_db_sync
   from models.activity import ActivityLog

   RULES = {
       "productive":    ["code.exe", "pycharm", "vscode",
                         "github.com", "stackoverflow.com", "jira"],
       "unproductive":  ["youtube.com", "facebook.com",
                         "twitter.com", "instagram.com", "netflix.com"],
   }

   def _classify(app_name: str, window_title: str) -> str:
       combined = f"{app_name} {window_title}".lower()
       for keyword in RULES["productive"]:
           if keyword in combined:
               return "productive"
       for keyword in RULES["unproductive"]:
           if keyword in combined:
               return "unproductive"
       return "neutral"

   @shared_task
   def classify_batch(user_id: int, events: list):
       with get_db_sync() as db:
           logs = []
           for e in events:
               category = _classify(
                   e.get("app_name", ""),
                   e.get("window_title", "")
               )
               logs.append(ActivityLog(
                   time=e["timestamp"],
                   user_id=user_id,
                   app_name=e["app_name"],
                   window_title=e["window_title"],
                   is_idle=e["is_idle"],
                   duration_sec=e.get("duration_sec", 60),
                   category=category,
               ))
           db.add_all(logs)
           db.commit()

WebSocket Yöneticisi
---------------------

.. code-block:: python

   # core/ws_manager.py
   from fastapi import APIRouter, WebSocket, WebSocketDisconnect
   from collections import defaultdict

   ws_router = APIRouter()

   class ConnectionManager:
       def __init__(self):
           self.connections: dict[int, list[WebSocket]] = defaultdict(list)

       async def connect(self, user_id: int, ws: WebSocket):
           await ws.accept()
           self.connections[user_id].append(ws)

       def disconnect(self, user_id: int, ws: WebSocket):
           self.connections[user_id].remove(ws)

       async def broadcast_user(self, user_id: int, message: dict):
           for ws in self.connections.get(user_id, []):
               await ws.send_json(message)

   manager = ConnectionManager()

   @ws_router.websocket("/ws/realtime")
   async def realtime(websocket: WebSocket, token: str):
       user = verify_ws_token(token)  # JWT doğrulama
       await manager.connect(user.id, websocket)
       try:
           while True:
               await websocket.receive_text()  # ping-pong canlı tut
       except WebSocketDisconnect:
           manager.disconnect(user.id, websocket)

Bağımlılıklar
--------------

.. code-block:: text

   fastapi>=0.111.0
   uvicorn[standard]>=0.29.0
   sqlalchemy[asyncio]>=2.0.0
   asyncpg>=0.29.0          # PostgreSQL async driver
   alembic>=1.13.0          # DB migration
   celery[redis]>=5.4.0     # Arka plan işleme
   redis>=5.0.0             # Cache + Celery broker
   python-jose[cryptography]>=3.3.0  # JWT
   passlib[bcrypt]>=1.7.4   # Şifre hashing
   python-multipart>=0.0.9  # Dosya yükleme
   pydantic-settings>=2.2.0 # Config yönetimi
