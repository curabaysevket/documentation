.. _desktime-agent:

========================
Masaüstü Ajanı
========================

Masaüstü ajanı, kullanıcının bilgisayarına kurulan hafif bir Python
uygulamasıdır. Arka planda çalışarak aktivite verilerini toplar,
yerel olarak tamponlar ve sunucuya periyodik olarak gönderir.

.. toctree::
   :maxdepth: 2

   implementation

Desteklenen Platformlar
------------------------

- **Windows 10/11** — ``pywin32`` + ``win32gui`` ile native pencere tespiti
- **Linux (X11)** — ``xdotool`` veya ``python-xlib`` ile pencere tespiti
- **Linux (Wayland)** — ``atspi`` (erişilebilirlik API) üzerinden sınırlı destek

Toplanan Veriler
-----------------

.. list-table::
   :header-rows: 1
   :widths: 30 40 30

   * - Veri
     - Yöntem
     - Örnek
   * - Aktif uygulama adı
     - OS Process API
     - ``code.exe``, ``firefox``
   * - Pencere başlığı
     - OS Window API
     - ``main.py - VSCode``
   * - Klavye/fare aktivitesi
     - ``pynput`` hooks
     - aktif / idle (boşta)
   * - Ekran görüntüsü
     - ``Pillow`` (PIL)
     - JPEG, isteğe bağlı blur
   * - URL (tarayıcı)
     - Pencere başlığından parse
     - ``github.com/user/repo``

Gönderim Döngüsü
-----------------

.. mermaid::

   sequenceDiagram
       participant OS as İşletim Sistemi
       participant Agent as Yerel Ajan
       participant SQLite as Offline SQLite
       participant API as Backend API

       loop Her 1 saniye
           OS->>Agent: Aktif pencere + aktivite durumu
           Agent->>SQLite: Ham veri kaydet
       end

       loop Her 60 saniye
           Agent->>Agent: Veriyi grupla/özet çıkar
           Agent->>API: POST /api/v1/ingest/activity
           alt Bağlantı başarısız
               Agent->>SQLite: Buffer'da tut
           else Başarılı
               SQLite->>Agent: Buffer temizle
           end
       end

       loop Her 5 dakika (isteğe bağlı)
           Agent->>API: POST /api/v1/ingest/screenshot
       end

Bağımlılıklar
--------------

.. code-block:: text

   pynput>=1.7.6          # Klavye/fare hook
   psutil>=5.9.0          # Cross-platform process bilgisi
   pywin32>=306           # Windows pencere API (sadece Windows)
   python-xlib>=0.33      # Linux X11 pencere API (sadece Linux)
   Pillow>=10.0.0         # Ekran görüntüsü
   httpx>=0.27.0          # Async HTTP istemci
   websockets>=12.0       # WebSocket bağlantısı
   cryptography>=42.0.0   # SQLite buffer şifreleme (AES-256)
   apscheduler>=3.10.0    # Zamanlayıcı (periyodik gönderim)
