# Aktivite Takip Sistemi — Implementasyon Kodu

Şirket içi DeskTime benzeri aktivite takip sisteminin tüm bileşenlerini içerir.

## Dizin Yapısı

```
code/
├── agent/                  # Windows masaüstü ajanı (Python)
│   ├── main.py             # Giriş noktası
│   ├── config.py           # Ortam değişkenleri ile yapılandırma
│   ├── requirements.txt    # pip bağımlılıkları
│   ├── tracker/
│   │   ├── window.py       # Aktif pencere tespiti (pywin32)
│   │   ├── exchange.py     # Exchange e-posta istatistikleri (EWS)
│   │   └── files.py        # Dosya açılış izleme (watchdog)
│   ├── sync/
│   │   └── client.py       # n8n webhook HTTP istemcisi
│   └── storage/
│       └── offline.py      # Şifreli SQLite offline buffer
│
├── extension/              # Chrome/Edge tarayıcı eklentisi (MV3)
│   ├── manifest.json
│   ├── background.js       # Web takibi + n8n gönderimi
│   └── popup.html          # Eklenti durumu popup'u
│
├── database/
│   └── sqlserver_schema.sql  # SQL Server tablo tanımları
│
├── n8n/                    # n8n workflow JSON'ları (import edilir)
│   ├── receive_activity.json
│   └── daily_report.json
│
└── mobile/
    ├── android_tasker.md   # Android Tasker kurulum rehberi
    └── ios_shortcut.md     # iOS Apple Shortcuts kurulum rehberi
```

## Hızlı Başlangıç

### 1. SQL Server Şemasını Oluştur
```sql
-- SQL Server Management Studio'da çalıştır:
-- database/sqlserver_schema.sql
```

### 2. n8n Workflow'larını Import Et
```
n8n UI → Settings → Import Workflow → n8n/ klasöründeki JSON'ları yükle
```

### 3. Masaüstü Ajanını Kur
```batch
pip install -r agent/requirements.txt

:: Ortam değişkenlerini ayarla
set N8N_BASE_URL=http://sunucu:5678
set AGENT_API_KEY=gizli-api-key
set AGENT_USER_ID=1
set EXCHANGE_USER=kullanici@sirket.com
set EXCHANGE_PASSWORD=sifre

python agent/main.py
```

### 4. Chrome Eklentisini Kur
1. `extension/background.js` dosyasında `N8N_WEBHOOK`, `API_KEY`, `USER_ID` değerlerini güncelle
2. Chrome → `chrome://extensions` → Geliştirici modu → "Yüklenmemiş uzantı yükle" → `extension/` klasörünü seç

### 5. Mobil Kurulum
- **Android:** `mobile/android_tasker.md` rehberini takip et
- **iOS:** `mobile/ios_shortcut.md` rehberini takip et

## Geliştirme Fazları

| Faz | Kapsam | Süre |
|-----|--------|------|
| 1 | Agent + Exchange + n8n + Telegram | Hafta 1-2 |
| 2 | Chrome/Edge eklentisi + web takibi | Hafta 2-3 |
| 3 | Mobil (Tasker + iOS Shortcuts) | Hafta 3 |
| 4 | Çok kullanıcı + Grafana dashboard | Hafta 4-5 |
| 5 | Haftalık e-posta raporu + PyInstaller .exe | Hafta 5-6 |
