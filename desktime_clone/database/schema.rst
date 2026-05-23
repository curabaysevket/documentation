.. _desktime-database-schema:

========================
Veritabanı Şeması
========================

İlişkisel Tablolar (PostgreSQL)
---------------------------------

.. code-block:: sql

   -- Şirketler
   CREATE TABLE companies (
       id         SERIAL PRIMARY KEY,
       name       TEXT NOT NULL,
       plan       TEXT DEFAULT 'free',  -- free, pro, enterprise
       created_at TIMESTAMPTZ DEFAULT NOW()
   );

   -- Kullanıcılar
   CREATE TABLE users (
       id            SERIAL PRIMARY KEY,
       company_id    INTEGER REFERENCES companies(id) ON DELETE CASCADE,
       email         TEXT UNIQUE NOT NULL,
       password_hash TEXT NOT NULL,
       role          TEXT DEFAULT 'employee',  -- admin, manager, employee
       is_active     BOOLEAN DEFAULT TRUE,
       created_at    TIMESTAMPTZ DEFAULT NOW()
   );
   CREATE INDEX idx_users_company ON users(company_id);

   -- Ekipler
   CREATE TABLE teams (
       id         SERIAL PRIMARY KEY,
       company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
       name       TEXT NOT NULL
   );

   CREATE TABLE team_members (
       team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
       user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
       PRIMARY KEY (team_id, user_id)
   );

   -- Üretkenlik kuralları
   CREATE TABLE productivity_rules (
       id         SERIAL PRIMARY KEY,
       company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
       app_name   TEXT NOT NULL,  -- "chrome.exe" veya "youtube.com"
       category   TEXT NOT NULL   -- productive | unproductive | neutral
   );
   CREATE INDEX idx_rules_company ON productivity_rules(company_id);

   -- Projeler ve görevler
   CREATE TABLE projects (
       id         SERIAL PRIMARY KEY,
       company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
       name       TEXT NOT NULL,
       is_active  BOOLEAN DEFAULT TRUE,
       created_at TIMESTAMPTZ DEFAULT NOW()
   );

   CREATE TABLE tasks (
       id            SERIAL PRIMARY KEY,
       project_id    INTEGER REFERENCES projects(id) ON DELETE CASCADE,
       user_id       INTEGER REFERENCES users(id) ON DELETE SET NULL,
       name          TEXT NOT NULL,
       total_seconds INTEGER DEFAULT 0
   );

   -- Ekran görüntüsü metadata
   CREATE TABLE screenshots (
       id          SERIAL PRIMARY KEY,
       user_id     INTEGER REFERENCES users(id) ON DELETE CASCADE,
       captured_at TIMESTAMPTZ NOT NULL,
       file_path   TEXT NOT NULL,  -- /data/screenshots/{user_id}/{date}/{id}.jpg
       is_blurred  BOOLEAN DEFAULT FALSE
   );
   CREATE INDEX idx_screenshots_user_time ON screenshots(user_id, captured_at DESC);

Zaman Serisi Tablo (TimescaleDB Hypertable)
--------------------------------------------

.. code-block:: sql

   -- TimescaleDB eklentisini etkinleştir
   CREATE EXTENSION IF NOT EXISTS timescaledb;

   -- Aktivite logları — tüm kullanıcı aktivitelerinin ana deposu
   CREATE TABLE activity_logs (
       time         TIMESTAMPTZ NOT NULL,
       user_id      INTEGER NOT NULL,
       app_name     TEXT,
       window_title TEXT,
       category     TEXT DEFAULT 'neutral',  -- productive | unproductive | neutral
       duration_sec INTEGER DEFAULT 60,
       is_idle      BOOLEAN DEFAULT FALSE
   );

   -- 1 günlük chunk ile hypertable oluştur
   SELECT create_hypertable('activity_logs', 'time', chunk_time_interval => INTERVAL '1 day');

   -- Sorgularda kullanılacak indeksler
   CREATE INDEX idx_activity_user_time ON activity_logs(user_id, time DESC);
   CREATE INDEX idx_activity_category  ON activity_logs(category, time DESC);

   -- 90 günden eski verileri otomatik sıkıştır
   ALTER TABLE activity_logs SET (
       timescaledb.compress,
       timescaledb.compress_segmentby = 'user_id'
   );
   SELECT add_compression_policy('activity_logs', INTERVAL '90 days');

Örnek Sorgular
---------------

**Günlük uygulama kullanım dağılımı:**

.. code-block:: sql

   SELECT
       app_name,
       SUM(duration_sec) AS total_seconds,
       category
   FROM activity_logs
   WHERE user_id = 42
     AND time >= CURRENT_DATE
     AND time <  CURRENT_DATE + INTERVAL '1 day'
     AND is_idle = FALSE
   GROUP BY app_name, category
   ORDER BY total_seconds DESC;

**Saatlik üretkenlik skoru (zaman çizelgesi):**

.. code-block:: sql

   SELECT
       time_bucket('1 hour', time) AS hour,
       SUM(CASE WHEN category = 'productive'   THEN duration_sec ELSE 0 END) AS productive_sec,
       SUM(CASE WHEN category = 'unproductive' THEN duration_sec ELSE 0 END) AS unproductive_sec,
       SUM(CASE WHEN is_idle = TRUE            THEN duration_sec ELSE 0 END) AS idle_sec
   FROM activity_logs
   WHERE user_id = 42
     AND time >= NOW() - INTERVAL '7 days'
   GROUP BY hour
   ORDER BY hour;

**Şirket geneli günlük özet:**

.. code-block:: sql

   SELECT
       u.id AS user_id,
       u.email,
       SUM(a.duration_sec) FILTER (WHERE a.category = 'productive')   AS productive_sec,
       SUM(a.duration_sec) FILTER (WHERE a.category = 'unproductive') AS unproductive_sec,
       SUM(a.duration_sec) FILTER (WHERE a.is_idle = TRUE)            AS idle_sec
   FROM activity_logs a
   JOIN users u ON u.id = a.user_id
   WHERE u.company_id = 1
     AND a.time >= CURRENT_DATE
   GROUP BY u.id, u.email;

Alembic Migration
------------------

.. code-block:: bash

   # İlk migration oluşturma
   alembic init alembic
   alembic revision --autogenerate -m "initial_schema"
   alembic upgrade head

   # Yeni migration eklemek
   alembic revision --autogenerate -m "add_leave_requests_table"
   alembic upgrade head

Redis Önbellek Şeması
----------------------

.. list-table::
   :header-rows: 1
   :widths: 40 20 40

   * - Anahtar (Key)
     - TTL
     - Değer
   * - ``dashboard:summary:user:{id}``
     - 60s
     - JSON: günlük özet istatistikleri
   * - ``dashboard:timeline:user:{id}:date:{date}``
     - 300s
     - JSON: saatlik aktivite zaman çizelgesi
   * - ``report:weekly:company:{id}``
     - 3600s
     - JSON: haftalık şirket raporu
   * - ``session:refresh:{token_hash}``
     - 7d
     - user_id: refresh token doğrulama
