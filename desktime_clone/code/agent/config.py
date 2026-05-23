import os

N8N_BASE_URL = os.environ.get("N8N_BASE_URL", "http://sunucu:5678")
API_KEY      = os.environ.get("AGENT_API_KEY", "degistir-beni")
USER_ID      = int(os.environ.get("AGENT_USER_ID", "1"))

EXCHANGE_URL      = os.environ.get("EXCHANGE_URL", "https://mail.sirket.com/EWS/Exchange.asmx")
EXCHANGE_USER     = os.environ.get("EXCHANGE_USER", "kullanici@sirket.com")
EXCHANGE_PASSWORD = os.environ.get("EXCHANGE_PASSWORD", "")

IDLE_THRESHOLD_SEC  = 300   # 5 dakika hareketsizlik → idle
COLLECT_INTERVAL    = 1     # saniyede bir pencere örnekle
SYNC_INTERVAL       = 60    # 60 saniyede bir n8n'e gönder
EXCHANGE_INTERVAL   = 900   # 15 dakikada bir Exchange sorgula

OFFLINE_DB_PATH = os.environ.get("OFFLINE_DB", "offline_buffer.db")
ENCRYPTION_KEY  = os.environ.get("ENCRYPTION_KEY", "").encode() or None

HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
