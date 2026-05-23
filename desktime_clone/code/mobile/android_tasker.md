# Android — Tasker ile Telefon Takibi

## Gereksinimler
- [Tasker](https://play.google.com/store/apps/details?id=net.dinglisch.android.taskerm) uygulaması (ücretli, ~3 USD)

## Kurulum Adımları

### 1. Yeni Profil Oluştur
1. Tasker → **Profiles** → **+**
2. Tetikleyici: **Event** → **Phone** → **Call End**
3. "New Task" → isim ver: `Aktivite Gönder`

### 2. Task Aksiyonlarını Ekle

**Aksiyon 1 — Değişkenleri Ayarla:**
```
Action: Variable Set
Name:  %N8N_URL
Value: http://SUNUCU_IP:5678/webhook/phone
```

```
Action: Variable Set
Name:  %USER_ID
Value: 1
```

**Aksiyon 2 — Arama Yönünü Belirle:**
```
Action: Variable Set
Name:  %DIRECTION
Value: %CNUM.length() > 0 ? outbound : inbound
```
*(Not: Tasker'da gelen/giden ayrımı için `%CNUM` değişkeni kontrol edilir.)*

**Aksiyon 3 — HTTP POST:**
```
Action: HTTP Request
Method: POST
URL:    %N8N_URL
Headers:
  Content-Type: application/json
  X-API-Key: BURAYA_API_KEY_YAZ
Body (JSON):
{
  "user_id": %USER_ID,
  "duration_sec": %Cduration,
  "direction": "%DIRECTION",
  "platform": "android"
}
```

### 3. Tasker Backup'ı Paylaşma (Ekip için)
1. Tasker → **Data** → **Backup**
2. `Tasker/configs/user/Aktivite Gönder.tsk` dosyasını paylaş
3. Diğer Android kullanıcı: **Restore** → Import → kendi `USER_ID` ve `API_KEY`'ini düzenle

## Değişken Notları
| Tasker Değişkeni | Anlamı |
|---|---|
| `%CNUM` | Aranan/arayan numara |
| `%CNAME` | Kişi adı (varsa) |
| `%CDATE` | Arama tarihi |
| `%CTIME` | Arama saati |
| `%CTYPE` | 0=gelen, 1=giden, 2=kaçırılan |
| `%CDURATION` | Görüşme süresi (saniye) |
