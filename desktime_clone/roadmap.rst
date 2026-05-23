.. _desktime-roadmap:

========================
Geliştirme Yol Haritası
========================

Özellikler MVP'den tam kapsama doğru öncelik sırasıyla geliştirilir.
Her aşama bir öncekinin üzerine inşa edilir ve bağımsız olarak test edilebilir.

Aşama 1 — Ajan Çekirdeği (1-2. Hafta)
---------------------------------------

**Hedef:** Windows ve Linux'ta çalışan, veri toplayan ve gönderen temel ajan.

.. list-table::
   :header-rows: 0
   :widths: 5 95

   * - ☐
     - ``core/window.py`` — Windows (win32gui) + Linux (xdotool) pencere tespiti
   * - ☐
     - ``core/activity.py`` — pynput ile klavye/fare idle tespiti
   * - ☐
     - ``core/storage.py`` — AES-256 şifreli SQLite offline buffer
   * - ☐
     - ``sync/api_client.py`` — httpx ile batch gönderim
   * - ☐
     - ``main.py`` — APScheduler ile 1s toplama / 60s gönderim döngüsü
   * - ☐
     - Config dosyası (server URL, API key, ayarlar)

**Test:** Ajanı çalıştır, 5 dakika bekle, SQLite'da veri biriktiğini doğrula.

Aşama 2 — Backend API + Veritabanı (3-4. Hafta)
-------------------------------------------------

**Hedef:** Ajandan veri alan, saklayan ve temel sorgu sunan API.

.. list-table::
   :header-rows: 0
   :widths: 5 95

   * - ☐
     - PostgreSQL + TimescaleDB kurulumu ve ``activity_logs`` hypertable
   * - ☐
     - SQLAlchemy modelleri + Alembic migration
   * - ☐
     - ``POST /api/v1/auth/token`` — JWT kimlik doğrulama
   * - ☐
     - ``POST /api/v1/ingest/activity`` — batch veri alma
   * - ☐
     - Celery + Redis: üretkenlik sınıflandırma worker
   * - ☐
     - ``GET /api/v1/dashboard/timeline`` — temel timeline sorgusu
   * - ☐
     - Docker Compose: db + redis + backend

**Test:** Ajanı gerçek sunucuya bağla, 1 gün veri topla, timeline sorgusunu çalıştır.

Aşama 3 — Frontend Dashboard (5-6. Hafta)
-------------------------------------------

**Hedef:** Aktivite ve üretkenlik verilerini görselleştiren web arayüzü.

.. list-table::
   :header-rows: 0
   :widths: 5 95

   * - ☐
     - React + TypeScript + Tailwind kurulumu
   * - ☐
     - Login sayfası + JWT token yönetimi
   * - ☐
     - ``ActivityTimeline`` bileşeni (saatlik aktivite şeridi)
     - ``ProductivityPieChart`` bileşeni (Recharts)
   * - ☐
     - ``AppUsageTable`` bileşeni (uygulama bazlı toplam süre)
   * - ☐
     - ``useRealtimeActivity`` hook (WebSocket)
   * - ☐
     - Raporlar sayfası (tarih aralığı seçici + grafikler)

**Test:** Dashboard'u aç, gerçek ajan verilerinin grafiklerde göründüğünü doğrula.

Aşama 4 — Ekran Görüntüsü Modülü (7. Hafta)
---------------------------------------------

.. list-table::
   :header-rows: 0
   :widths: 5 95

   * - ☐
     - ``core/screenshot.py`` — Pillow ile 5 dakikada bir ekran görüntüsü
   * - ☐
     - Blur seçeneği (GaussianBlur, konfigüre edilebilir)
   * - ☐
     - ``POST /api/v1/ingest/screenshot`` — multipart upload endpoint
   * - ☐
     - Celery worker: JPEG sıkıştırma + dosya sistemi kayıt
   * - ☐
     - ``Screenshots.tsx`` — grid galeri + büyütme modalı

Aşama 5 — Çok Kullanıcı & Ekip Yönetimi (8-9. Hafta)
------------------------------------------------------

.. list-table::
   :header-rows: 0
   :widths: 5 95

   * - ☐
     - Şirket / ekip / kullanıcı tabloları
   * - ☐
     - RBAC: Admin / Manager / Employee rolleri
   * - ☐
     - ``TeamAdmin.tsx`` — kullanıcı ekleme, ekip oluşturma
   * - ☐
     - Üretkenlik kuralı yönetimi UI
   * - ☐
     - Ekip bazlı rapor sorguları

Aşama 6 — Docker Paketleme & Ajan Dağıtımı (9. Hafta)
-------------------------------------------------------

.. list-table::
   :header-rows: 0
   :widths: 5 95

   * - ☐
     - Tam ``docker-compose.yml`` (db + redis + backend + worker + frontend + nginx)
   * - ☐
     - PyInstaller ile Windows .exe ajan paketi
   * - ☐
     - PyInstaller ile Linux AppImage ajan paketi
   * - ☐
     - Kurulum betiği + yedekleme betiği
   * - ☐
     - ``.env.example`` + kurulum dokümantasyonu

Aşama 7 — Proje Takibi & İzin Yönetimi (10. Hafta)
----------------------------------------------------

.. list-table::
   :header-rows: 0
   :widths: 5 95

   * - ☐
     - Proje / görev tabloları
   * - ☐
     - Manuel zamanlayıcı API (start/stop)
   * - ☐
     - ``Projects.tsx`` — proje bazlı raporlama
   * - ☐
     - İzin takvimi (tatil, hastalık izni) tabloları ve UI

Aşama 8 — Entegrasyonlar (11. Hafta+)
---------------------------------------

.. list-table::
   :header-rows: 0
   :widths: 5 95

   * - ☐
     - Jira entegrasyonu (aktif ticket'ı otomatik proje olarak logla)
   * - ☐
     - Google Calendar entegrasyonu (toplantı sürelerini takip et)
   * - ☐
     - Slack bildirimleri (günlük özet mesajı)
   * - ☐
     - REST API dışa aktarma (üçüncü parti entegrasyon desteği)

Genel Takvim Özeti
-------------------

.. list-table::
   :header-rows: 1
   :widths: 15 20 65

   * - Hafta
     - Aşama
     - Çıktı
   * - 1-2
     - Ajan Çekirdeği
     - Çalışan ajan, SQLite buffer, API gönderim
   * - 3-4
     - Backend + DB
     - Veri alan ve saklayan API, Celery worker
   * - 5-6
     - Frontend
     - Dashboard, grafikler, gerçek zamanlı güncelleme
   * - 7
     - Ekran Görüntüsü
     - Blur seçenekli ekran görüntüsü galerisi
   * - 8-9
     - Ekip Yönetimi
     - Çok kullanıcı, roller, ekip raporları
   * - 9
     - Docker Paketi
     - Tek komutla self-hosted kurulum
   * - 10
     - Projeler & İzin
     - Manuel zamanlayıcı, tatil takvimi
   * - 11+
     - Entegrasyonlar
     - Jira, Google Calendar, Slack
