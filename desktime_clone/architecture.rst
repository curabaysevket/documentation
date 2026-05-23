.. _desktime-architecture:

========================
Mimari Genel Bakış
========================

Sistem, istemci-sunucu (Client-Server) modeline dayanan, olay güdümlü
(event-driven) dağıtık bir mimariye sahiptir. Veri işleme yükü yerel
masaüstü ajanı ile self-hosted bulut sunucusu arasında paylaştırılmıştır.

Katmanlar
---------

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Katman
     - Teknoloji
     - Sorumluluk
   * - Masaüstü Ajanı
     - Python 3.11 + PyInstaller
     - OS API hooks, aktivite/ekran görüntüsü toplama, offline SQLite buffer
   * - Ağ Katmanı
     - HTTPS (TLS 1.3) + WebSocket
     - Şifreli veri taşıma, gerçek zamanlı panel güncellemeleri
   * - Backend API
     - FastAPI + Uvicorn
     - REST endpoint'leri, JWT kimlik doğrulama, WebSocket hub
   * - İşleme Motoru
     - Celery + Redis
     - Üretkenlik sınıflandırma, ekran görüntüsü işleme
   * - Veritabanı
     - PostgreSQL 16 + TimescaleDB
     - İlişkisel veriler + zaman serisi aktivite logları
   * - Önbellek
     - Redis 7
     - API cache, Celery broker, oturum yönetimi
   * - Frontend
     - React 18 + TypeScript + Tailwind CSS
     - Yönetim paneli, raporlar, gerçek zamanlı grafikler
   * - Altyapı
     - Docker Compose + Nginx
     - Self-hosted kurulum, SSL sonlandırma, statik dosya servisi

Veri Akış Şeması
-----------------

.. mermaid::

   flowchart TD
       A["Kullanıcı Bilgisayarı\n(Windows / Linux)"] -->|OS API Hooks| B
       B["DeskTime Yerel Ajanı\n(Python)"]
       B -->|"Offline SQLite Buffer\n(Bağlantı yokken)"| B
       B -->|"TLS/SSL Şifreli\nJSON Paketleri"| C
       C["Nginx\nReverse Proxy"]
       C --> D["Yük Dengeleyici /\nAPI Gateway\n(FastAPI)"]
       D --> E["Mesaj Kuyruğu\n(Redis + Celery)"]
       E --> F["Üretkenlik\nİşleme Motoru"]
       F --> G["Zaman Serisi DB\n(TimescaleDB)\nAktivite Logları"]
       F --> H["İlişkisel DB\n(PostgreSQL)\nKullanıcı & Şirket"]
       F --> I["Dosya Sistemi\nEkran Görüntüleri"]
       G --> J
       H --> J
       I --> J
       J["Web Dashboard\n(React)\nRaporlar & Yönetim"]
       J -->|"WebSocket\nGerçek Zamanlı"| D

Güvenlik Katmanları
--------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Katman
     - Uygulama
   * - Aktarım güvenliği (in-transit)
     - TLS 1.3 / HTTPS — tüm ajan ↔ sunucu trafiği
   * - Depolama güvenliği (at-rest)
     - AES-256 — ekran görüntüleri ve SQLite offline buffer
   * - Kimlik doğrulama
     - JWT access token (15 dk) + refresh token (7 gün)
   * - Yetkilendirme
     - RBAC: Admin / Manager / Employee rolleri
   * - Uyumluluk
     - GDPR: kullanıcı veri silme endpoint'i, veri saklama politikası

Ölçeklenebilirlik
------------------

Self-hosted tek sunucu kurulumu için sistem şu kapasiteyi karşılar:

- **50–200 eşzamanlı ajan** bağlantısı (orta güçlü PC ile)
- **TimescaleDB** otomatik partition ile yıllarca aktivite logu depolama
- **Celery worker sayısı** iş yüküne göre yatay ölçeklenebilir
- Büyümek gerekirse Docker Compose → Kubernetes geçişi mümkündür
