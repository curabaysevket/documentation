.. _desktime-clone:

====================================
DeskTime Benzeri Zaman Takip Sistemi
====================================

Bu bölüm, DeskTime'ın tüm özelliklerini kapsayan self-hosted, açık kaynaklı
bir zaman ve üretkenlik takip sisteminin mimari dokümantasyonunu içermektedir.

Sistem; Windows ve Linux masaüstü ajanı, FastAPI tabanlı backend, PostgreSQL +
TimescaleDB veritabanı katmanı ve React tabanlı yönetim paneliyle birlikte
Docker Compose ile tek komutla kurulabilir.

.. toctree::
   :maxdepth: 2

   architecture
   agent/index
   backend/index
   database/index
   frontend/index
   deployment/index
   roadmap
