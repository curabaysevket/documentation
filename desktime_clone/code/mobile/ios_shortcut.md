# iOS — Apple Shortcuts ile Telefon Takibi

## Kısıtlamalar
iOS gizlilik politikası nedeniyle: kişi adı ve numara alınamaz.
Sadece **görüşme süresi + saat** gönderilebilir.

## Kurulum Adımları

### 1. Kısayol Oluştur
Kısayollar uygulaması → **+** (Yeni Kısayol)

**Eylemler:**

```
1. "Metin" bloğu ekle:
   {
     "user_id": 1,
     "duration_sec": 0,
     "direction": "unknown",
     "platform": "ios",
     "note": "ios-shortcut"
   }
   (iOS arama süresi otomatik alınamaz, kullanıcı manuel girer)

2. "URL" bloğu ekle:
   http://SUNUCU_IP:5678/webhook/phone

3. "Web isteği yap" bloğu ekle:
   Yöntem: POST
   Başlıklar: Content-Type: application/json
              X-API-Key: BURAYA_API_KEY
   İstek gövdesi: Metin (yukarıdaki JSON)
```

### 2. Otomasyon Olarak Ayarla (Tercih edilen)
Kısayollar → **Otomasyon** → **+** → **Kişisel Otomasyon**
- Tetikleyici: **Uygulama** → **Telefon** → **Kapatıldığında**
- Eylem: Yukarıdaki kısayolu çalıştır
- "Çalıştırmadan önce sor" → **Kapat** (otomatik çalışsın)

### 3. Ekip Dağıtımı
1. Kısayolu oluşturun
2. **Paylaş** → iCloud linki kopyala → WhatsApp/mail ile dağıt
3. Her kullanıcı: Kısayolu indir → `user_id` ve `API_KEY` bloğunu kendi bilgileriyle güncelle

## Not
iOS'ta arama süresi otomatik olarak alınamadığından, bu entegrasyon
"arama yapıldı" olayını kaydeder (süre = 0). Telefon raporlarının
%80'i Android kullanıcılarından gelir, iOS raporlama isteğe bağlıdır.

Daha gelişmiş iOS takibi için: **Screen Time API** (Apple MDM) kurumsal
gerektirir ve sadece yönetilen cihazlarda çalışır.
