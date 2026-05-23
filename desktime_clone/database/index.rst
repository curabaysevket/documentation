.. _desktime-database:

========================
Veritabanı Katmanı
========================

Sistem, Polyglot Persistence yaklaşımı yerine tek bir PostgreSQL motorunda
hem ilişkisel hem de zaman serisi verileri yönetir. TimescaleDB eklentisi
sayesinde aktivite logları için optimize edilmiş hypertable yapısı kullanılır.

.. toctree::
   :maxdepth: 2

   schema

Neden PostgreSQL + TimescaleDB?
---------------------------------

Self-hosted senaryo için iki ayrı veritabanı motoru (PostgreSQL + InfluxDB)
çalıştırmak yerine TimescaleDB tercih edilmiştir:

- **Tek motor** — kurulum, yedekleme, izleme daha basit
- **SQL uyumluluğu** — standart JOIN ve aggregate sorguları çalışır
- **Otomatik partition** — ``time`` sütununa göre veri otomatik bölümlenir
- **Zaman aralığı sorguları** — ``time_bucket()`` ile verimli gruplama
- **Veri sıkıştırma** — eski veriler otomatik sıkıştırılır (disk tasarrufu)

Tablo Haritası
---------------

.. mermaid::

   erDiagram
       companies {
           int id PK
           string name
           string plan
           timestamp created_at
       }
       users {
           int id PK
           int company_id FK
           string email
           string password_hash
           string role
           bool is_active
       }
       teams {
           int id PK
           int company_id FK
           string name
       }
       team_members {
           int team_id FK
           int user_id FK
       }
       productivity_rules {
           int id PK
           int company_id FK
           string app_name
           string category
       }
       projects {
           int id PK
           int company_id FK
           string name
           bool is_active
       }
       tasks {
           int id PK
           int project_id FK
           int user_id FK
           string name
           int total_seconds
       }
       activity_logs {
           timestamp time PK
           int user_id FK
           string app_name
           string window_title
           string category
           int duration_sec
           bool is_idle
       }
       screenshots {
           int id PK
           int user_id FK
           timestamp captured_at
           string file_path
           bool is_blurred
       }

       companies ||--o{ users : "has"
       companies ||--o{ teams : "has"
       companies ||--o{ productivity_rules : "defines"
       companies ||--o{ projects : "owns"
       teams ||--o{ team_members : "contains"
       users ||--o{ team_members : "member of"
       users ||--o{ activity_logs : "generates"
       users ||--o{ screenshots : "has"
       projects ||--o{ tasks : "has"
       users ||--o{ tasks : "works on"

Performans Hedefleri
---------------------

.. list-table::
   :header-rows: 1
   :widths: 40 30 30

   * - Sorgu
     - Hedef Süre
     - Yöntem
   * - Günlük aktivite zaman çizelgesi (1 kullanıcı)
     - < 50ms
     - TimescaleDB hypertable + user_id indeksi
   * - Haftalık üretkenlik raporu (50 kullanıcı)
     - < 200ms
     - ``time_bucket()`` + Redis cache
   * - Tüm şirket anlık özet
     - < 100ms
     - Redis önbellekleme (30s TTL)
   * - 1 yıllık aktivite logu depolama (100 kullanıcı)
     - ~50 GB
     - TimescaleDB sıkıştırma ile ~10 GB'a düşer
