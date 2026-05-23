-- ============================================================
-- Aktivite Takip Sistemi — SQL Server Şeması
-- ============================================================

-- Kullanıcılar
CREATE TABLE users (
    id         INT           PRIMARY KEY IDENTITY,
    name       NVARCHAR(100) NOT NULL,
    email      NVARCHAR(200) NOT NULL,
    role       NVARCHAR(20)  NOT NULL DEFAULT 'employee',  -- admin, manager, employee
    api_key    NVARCHAR(64)  NOT NULL,
    is_active  BIT           NOT NULL DEFAULT 1,
    created_at DATETIME2     NOT NULL DEFAULT GETDATE(),
    CONSTRAINT uq_users_email   UNIQUE (email),
    CONSTRAINT uq_users_api_key UNIQUE (api_key),
    CONSTRAINT ck_users_role    CHECK (role IN ('admin', 'manager', 'employee'))
);

-- Uygulama/pencere aktivitesi
CREATE TABLE activity_logs (
    id           BIGINT        PRIMARY KEY IDENTITY,
    user_id      INT           NOT NULL REFERENCES users(id),
    logged_at    DATETIME2     NOT NULL,
    app_name     NVARCHAR(200),
    window_title NVARCHAR(500),
    duration_sec INT           NOT NULL DEFAULT 1,
    is_idle      BIT           NOT NULL DEFAULT 0,
    category     NVARCHAR(50)  NOT NULL DEFAULT 'other'
        CONSTRAINT ck_activity_category CHECK (category IN ('work', 'idle', 'social', 'entertainment', 'other'))
);
CREATE INDEX idx_activity_user_date ON activity_logs (user_id, logged_at);

-- Web geçmişi (tarayıcı eklentisinden)
CREATE TABLE web_history (
    id           BIGINT        PRIMARY KEY IDENTITY,
    user_id      INT           NOT NULL REFERENCES users(id),
    visited_at   DATETIME2     NOT NULL,
    url          NVARCHAR(1000),
    domain       NVARCHAR(200),
    page_title   NVARCHAR(500),
    duration_sec INT           NOT NULL DEFAULT 0,
    category     NVARCHAR(50)  NOT NULL DEFAULT 'other'
        CONSTRAINT ck_web_category CHECK (category IN ('work', 'social', 'news', 'entertainment', 'other'))
);
CREATE INDEX idx_web_user_date ON web_history (user_id, visited_at);

-- E-posta özeti (Exchange'den)
CREATE TABLE email_logs (
    id             BIGINT    PRIMARY KEY IDENTITY,
    user_id        INT       NOT NULL REFERENCES users(id),
    logged_at      DATETIME2 NOT NULL,
    received_count INT       NOT NULL DEFAULT 0,
    sent_count     INT       NOT NULL DEFAULT 0,
    read_count     INT       NOT NULL DEFAULT 0
);
CREATE INDEX idx_email_user_date ON email_logs (user_id, logged_at);

-- Telefon görüşmeleri (Android Tasker / iOS Shortcuts)
CREATE TABLE phone_logs (
    id           BIGINT        PRIMARY KEY IDENTITY,
    user_id      INT           NOT NULL REFERENCES users(id),
    called_at    DATETIME2     NOT NULL,
    duration_sec INT           NOT NULL DEFAULT 0,
    direction    NVARCHAR(10)  NOT NULL DEFAULT 'unknown'
        CONSTRAINT ck_phone_direction CHECK (direction IN ('inbound', 'outbound', 'unknown')),
    platform     NVARCHAR(10)  NOT NULL DEFAULT 'unknown'
        CONSTRAINT ck_phone_platform CHECK (platform IN ('android', 'ios', 'unknown'))
);
CREATE INDEX idx_phone_user_date ON phone_logs (user_id, called_at);

-- Dosya açılış olayları (Excel, Word, Netcad vs.)
CREATE TABLE file_events (
    id         BIGINT        PRIMARY KEY IDENTITY,
    user_id    INT           NOT NULL REFERENCES users(id),
    event_at   DATETIME2     NOT NULL,
    file_path  NVARCHAR(1000),
    app_name   NVARCHAR(200),
    event_type NVARCHAR(20)  NOT NULL DEFAULT 'opened'
        CONSTRAINT ck_file_event_type CHECK (event_type IN ('opened', 'closed', 'created', 'modified'))
);
CREATE INDEX idx_file_user_date ON file_events (user_id, event_at);

-- ============================================================
-- Örnek Sorgular
-- ============================================================

-- Günlük uygulama kullanımı
-- SELECT app_name, SUM(duration_sec) AS toplam_sn, category
-- FROM activity_logs
-- WHERE user_id = 1
--   AND CAST(logged_at AS DATE) = CAST(GETDATE() AS DATE)
--   AND is_idle = 0
-- GROUP BY app_name, category
-- ORDER BY toplam_sn DESC;

-- Ekip günlük özeti (yönetici için)
-- SELECT u.name, u.email,
--        SUM(a.duration_sec) AS toplam_sn,
--        SUM(CASE WHEN a.category = 'work' THEN a.duration_sec ELSE 0 END) AS uretken_sn
-- FROM activity_logs a
-- JOIN users u ON u.id = a.user_id
-- WHERE CAST(a.logged_at AS DATE) = CAST(GETDATE() AS DATE)
-- GROUP BY u.name, u.email
-- ORDER BY toplam_sn DESC;
