.. _desktime-deployment:

========================
Kurulum & Dağıtım
========================

Sistem, tek bir ``docker compose up -d`` komutuyla kişisel PC veya sunucuya
kurulabilir. Tüm bileşenler Docker container olarak izole çalışır.

.. toctree::
   :maxdepth: 2

   docker

Gereksinimler
--------------

**Sunucu (minimum):**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Kaynak
     - Değer
   * - CPU
     - 2 çekirdek (4 önerilir)
   * - RAM
     - 4 GB (8 GB önerilir — 50+ kullanıcı için)
   * - Disk
     - 50 GB SSD (aktivite logları + ekran görüntüleri için)
   * - OS
     - Ubuntu 22.04 LTS / Debian 12 / Windows Server 2019+
   * - Docker
     - Docker Engine 24.0+ + Docker Compose v2

**Ağ:**

- Sunucuya erişilebilir sabit IP veya DDNS
- 80/443 portları açık (LAN içi kurulum için 80 yeterli)
- Ajan makinelerden sunucuya HTTPS erişimi

Servis Listesi
---------------

.. mermaid::

   graph LR
       subgraph "Docker Compose Stack"
           N["Nginx\n:80/:443"]
           B["FastAPI Backend\n:8000"]
           W["Celery Worker"]
           F["React Frontend\n(Nginx static)"]
           DB["PostgreSQL + TimescaleDB\n:5432"]
           R["Redis\n:6379"]
       end
       Internet -->|HTTPS| N
       N -->|"/api/"| B
       N -->|"/"| F
       B --> DB
       B --> R
       W --> DB
       W --> R

Hızlı Kurulum
--------------

.. code-block:: bash

   # 1. Repoyu klonla
   git clone https://github.com/kullanici/desktime-clone.git
   cd desktime-clone

   # 2. Ortam değişkenlerini ayarla
   cp .env.example .env
   # .env dosyasını düzenle (DB şifresi, JWT secret, domain adı)

   # 3. Tüm servisleri başlat
   docker compose up -d

   # 4. Veritabanı migration
   docker compose exec backend alembic upgrade head

   # 5. İlk admin kullanıcısını oluştur
   docker compose exec backend python -m scripts.create_admin

   # Dashboard: http://localhost (veya sunucu IP'si)

Ajan Kurulumu
--------------

**Windows:**

.. code-block:: bash

   # desktime-agent-setup.exe indir ve çalıştır
   # Kurulum sırasında sunucu URL ve API key gir:
   Server URL: https://sunucunuz.local
   API Key:    (dashboard'dan kopyala)

**Linux:**

.. code-block:: bash

   # AppImage indir
   chmod +x desktime-agent-x86_64.AppImage
   ./desktime-agent-x86_64.AppImage --server https://sunucunuz.local --key API_KEY

   # Otomatik başlatma için systemd servisi
   sudo cp desktime-agent.service /etc/systemd/system/
   sudo systemctl enable --now desktime-agent

Güncelleme
-----------

.. code-block:: bash

   git pull origin main
   docker compose pull
   docker compose up -d
   docker compose exec backend alembic upgrade head

Yedekleme
----------

.. code-block:: bash

   # PostgreSQL yedeği
   docker compose exec db pg_dump -U postgres desktime > backup_$(date +%Y%m%d).sql

   # Ekran görüntüleri yedeği
   tar -czf screenshots_$(date +%Y%m%d).tar.gz ./data/screenshots/

   # Otomatik yedekleme (cron)
   0 2 * * * /opt/desktime/scripts/backup.sh
