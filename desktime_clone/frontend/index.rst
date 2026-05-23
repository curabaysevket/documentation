.. _desktime-frontend:

========================
Frontend Dashboard
========================

Yöneticilerin ve çalışanların analiz raporlarına, ekip verilerine ve ekran
görüntülerine eriştiği React tabanlı web arayüzüdür.

.. toctree::
   :maxdepth: 2

   implementation

Teknoloji Yığını
-----------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Kütüphane
     - Amaç
   * - React 18 + TypeScript
     - Temel UI framework
   * - Tailwind CSS
     - Utility-first stillendirme
   * - Recharts
     - Aktivite grafikleri, pie chart, zaman çizelgesi
   * - React Query (TanStack Query)
     - Sunucu durumu yönetimi, otomatik yenileme
   * - Zustand
     - Küçük global state (kullanıcı oturumu, tema)
   * - React Router v6
     - Sayfa yönlendirme
   * - date-fns
     - Tarih formatlama ve hesaplama
   * - Axios
     - HTTP istemcisi

Sayfa Yapısı
-------------

.. mermaid::

   graph TD
       A[Login] --> B[Dashboard]
       B --> C[Raporlar]
       B --> D[Ekran Görüntüleri]
       B --> E[Projeler]
       B --> F[Ekip Yönetimi]
       F --> G[Kullanıcı Detayı]
       F --> H[Üretkenlik Kuralları]
       F --> I[İzin Yönetimi]

Dashboard Ana Sayfası
----------------------

Dashboard, kullanıcının bugünkü aktivitesini gerçek zamanlı olarak gösterir:

- **Zaman çizelgesi şeridi** — saatlik aktivite blokları (renkli: üretken/nötr/idle)
- **Uygulama dağılımı** — pie chart: en çok kullanılan uygulamalar
- **Üretkenlik skoru** — bugünkü yüzde göstergesi
- **Ekip canlı görünümü** — hangi kullanıcı şu an aktif (yöneticiler için)
- **Son ekran görüntüleri** — küçük önizleme kartları

Raporlar Sayfası
-----------------

- Tarih aralığı seçici (bugün / bu hafta / bu ay / özel)
- Kullanıcı veya ekip bazlı filtreleme
- Bar chart: günlük üretken/üretken değil/idle dağılımı
- Tablo: uygulama bazlı toplam süre listesi
- CSV/PDF dışa aktarma

Ekran Görüntüleri Sayfası
--------------------------

- Grid galeri görünümü (zaman damgalı)
- Büyütme modalı
- Blur/net filtresi
- Tarih navigasyonu

Projeler Sayfası
-----------------

- Proje listesi + ilerleme çubuğu
- Görev bazlı zamanlayıcı (başlat/durdur)
- Manuel süre girişi

Rol Tabanlı Erişim
-------------------

.. list-table::
   :header-rows: 1
   :widths: 30 25 25 20

   * - Sayfa / Özellik
     - Admin
     - Manager
     - Employee
   * - Kendi raporları
     - ✓
     - ✓
     - ✓
   * - Ekip raporları
     - ✓
     - ✓
     - ✗
   * - Ekran görüntüleri (kendi)
     - ✓
     - ✓
     - ✓
   * - Ekran görüntüleri (ekip)
     - ✓
     - ✓
     - ✗
   * - Kullanıcı yönetimi
     - ✓
     - ✗
     - ✗
   * - Üretkenlik kuralları
     - ✓
     - ✗
     - ✗
   * - Faturalama
     - ✓
     - ✗
     - ✗
