.. _desktime-backend:

========================
Backend API Katmanı
========================

Backend, FastAPI üzerine kurulu async bir REST API sunucusudur. Masaüstü
ajanlardan gelen veri akışını alır, Celery kuyruğuna iletir ve frontend
dashboard'una rapor verileri sağlar.

.. toctree::
   :maxdepth: 2

   implementation

API Endpoint Listesi
---------------------

**Kimlik Doğrulama**

.. list-table::
   :header-rows: 1
   :widths: 15 40 45

   * - Metod
     - Endpoint
     - Açıklama
   * - POST
     - ``/api/v1/auth/token``
     - Kullanıcı adı/şifre ile JWT access + refresh token alma
   * - POST
     - ``/api/v1/auth/refresh``
     - Refresh token ile yeni access token alma
   * - POST
     - ``/api/v1/auth/logout``
     - Refresh token geçersiz kılma

**Ajan Veri Gönderimi**

.. list-table::
   :header-rows: 1
   :widths: 15 40 45

   * - Metod
     - Endpoint
     - Açıklama
   * - POST
     - ``/api/v1/ingest/activity``
     - Aktivite olayları toplu gönderimi (batch)
   * - POST
     - ``/api/v1/ingest/screenshot``
     - Ekran görüntüsü yükleme (multipart/form-data)
   * - GET
     - ``/api/v1/agent/config``
     - Ajan yapılandırması (screenshot sıklığı, blur ayarı vb.)

**Dashboard & Raporlar**

.. list-table::
   :header-rows: 1
   :widths: 15 40 45

   * - Metod
     - Endpoint
     - Açıklama
   * - GET
     - ``/api/v1/dashboard/timeline``
     - Günlük aktivite zaman çizelgesi
   * - GET
     - ``/api/v1/dashboard/summary``
     - Günlük/haftalık özet istatistikler
   * - GET
     - ``/api/v1/reports/daily``
     - Günlük uygulama kullanım raporu
   * - GET
     - ``/api/v1/reports/productivity``
     - Üretkenlik skoru ve dağılımı
   * - GET
     - ``/api/v1/screenshots``
     - Ekran görüntüsü listesi (sayfalı)
   * - GET
     - ``/api/v1/screenshots/{id}``
     - Tekil ekran görüntüsü

**Ekip & Kullanıcı Yönetimi**

.. list-table::
   :header-rows: 1
   :widths: 15 40 45

   * - Metod
     - Endpoint
     - Açıklama
   * - GET/POST
     - ``/api/v1/teams``
     - Ekip listeleme / oluşturma
   * - GET/PUT/DELETE
     - ``/api/v1/users/{id}``
     - Kullanıcı detay / güncelleme / silme
   * - GET/POST
     - ``/api/v1/productivity-rules``
     - Üretkenlik kuralı yönetimi

**Proje Takibi**

.. list-table::
   :header-rows: 1
   :widths: 15 40 45

   * - Metod
     - Endpoint
     - Açıklama
   * - GET/POST
     - ``/api/v1/projects``
     - Proje listeleme / oluşturma
   * - POST
     - ``/api/v1/projects/{id}/timer/start``
     - Manuel proje zamanlayıcı başlat
   * - POST
     - ``/api/v1/projects/{id}/timer/stop``
     - Manuel proje zamanlayıcı durdur

**WebSocket**

.. list-table::
   :header-rows: 1
   :widths: 15 40 45

   * - Protokol
     - Endpoint
     - Açıklama
   * - WS
     - ``/ws/realtime``
     - Gerçek zamanlı aktivite güncellemeleri (dashboard)

Üretkenlik Motoru
------------------

Celery worker, kuyruktan gelen ham aktivite verisini şirketin tanımladığı
kurallara göre sınıflandırır:

.. mermaid::

   flowchart LR
       A["Ham Veri\napp='chrome.exe'\ntitle='Stack Overflow'"] --> B{Kural Motoru}
       B -->|"Üretken URL listesi\ngithub.com, stackoverflow.com"| C["✓ Üretken"]
       B -->|"Üretken Olmayan listesi\nyoutube.com, twitter.com"| D["✗ Üretken Değil"]
       B -->|"Eşleşme yok"| E["Nötr"]
       C --> F[(TimescaleDB\nAktivite Logu)]
       D --> F
       E --> F
