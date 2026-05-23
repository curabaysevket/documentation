.. _desktime-docker:

========================
Docker Compose Yapılandırması
========================

Tam ``docker-compose.yml``
----------------------------

.. code-block:: yaml

   version: '3.9'

   services:

     db:
       image: timescale/timescaledb:latest-pg16
       container_name: desktime_db
       restart: unless-stopped
       environment:
         POSTGRES_DB:       desktime
         POSTGRES_USER:     ${DB_USER}
         POSTGRES_PASSWORD: ${DB_PASSWORD}
       volumes:
         - pgdata:/var/lib/postgresql/data
       ports:
         - "127.0.0.1:5432:5432"   # Sadece localhost erişimi
       healthcheck:
         test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
         interval: 10s
         retries: 5

     redis:
       image: redis:7-alpine
       container_name: desktime_redis
       restart: unless-stopped
       command: redis-server --requirepass ${REDIS_PASSWORD}
       volumes:
         - redisdata:/data
       ports:
         - "127.0.0.1:6379:6379"

     backend:
       build: ./backend
       container_name: desktime_backend
       restart: unless-stopped
       environment:
         DATABASE_URL: postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@db:5432/desktime
         REDIS_URL:    redis://:${REDIS_PASSWORD}@redis:6379/0
         SECRET_KEY:   ${JWT_SECRET}
         SCREENSHOTS_DIR: /data/screenshots
       volumes:
         - screenshots:/data/screenshots
       depends_on:
         db:    { condition: service_healthy }
         redis: { condition: service_started }
       expose:
         - "8000"

     worker:
       build: ./backend
       container_name: desktime_worker
       restart: unless-stopped
       command: celery -A workers worker --loglevel=info --concurrency=4
       environment:
         DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/desktime
         REDIS_URL:    redis://:${REDIS_PASSWORD}@redis:6379/0
         SCREENSHOTS_DIR: /data/screenshots
       volumes:
         - screenshots:/data/screenshots
       depends_on:
         - backend
         - redis
         - db

     frontend:
       build:
         context: ./frontend
         args:
           VITE_API_URL: ${DOMAIN}
           VITE_WS_URL:  ${DOMAIN}
       container_name: desktime_frontend
       restart: unless-stopped
       expose:
         - "80"

     nginx:
       image: nginx:alpine
       container_name: desktime_nginx
       restart: unless-stopped
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf:ro
         - ./certs:/etc/nginx/certs:ro       # SSL sertifikaları
         - screenshots:/data/screenshots:ro  # Ekran görüntüsü static serve
       depends_on:
         - backend
         - frontend

   volumes:
     pgdata:
     redisdata:
     screenshots:

``.env.example``
-----------------

.. code-block:: bash

   # Veritabanı
   DB_USER=desktime
   DB_PASSWORD=guclu_bir_sifre_girin

   # Redis
   REDIS_PASSWORD=redis_sifresi

   # JWT
   JWT_SECRET=en_az_32_karakter_rastgele_string

   # Domain (SSL ile)
   DOMAIN=https://takip.sirketiniz.com
   # Veya LAN içi:
   # DOMAIN=http://192.168.1.100

``nginx.conf``
---------------

.. code-block:: nginx

   events {}

   http {
       upstream backend  { server backend:8000; }
       upstream frontend { server frontend:80;  }

       server {
           listen 80;
           server_name _;

           # HTTPS yönlendirmesi (SSL aktifse)
           # return 301 https://$host$request_uri;

           location /api/ {
               proxy_pass         http://backend;
               proxy_set_header   Host $host;
               proxy_set_header   X-Real-IP $remote_addr;
           }

           location /ws/ {
               proxy_pass         http://backend;
               proxy_http_version 1.1;
               proxy_set_header   Upgrade $http_upgrade;
               proxy_set_header   Connection "upgrade";
           }

           location /screenshots/ {
               alias /data/screenshots/;
               internal;  # Sadece backend yönlendirmesiyle erişilebilir
           }

           location / {
               proxy_pass http://frontend;
           }
       }
   }

``backend/Dockerfile``
-----------------------

.. code-block:: dockerfile

   FROM python:3.11-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

``frontend/Dockerfile``
------------------------

.. code-block:: dockerfile

   FROM node:20-alpine AS builder
   WORKDIR /app
   COPY package*.json .
   RUN npm ci
   COPY . .
   ARG VITE_API_URL
   ARG VITE_WS_URL
   RUN npm run build

   FROM nginx:alpine
   COPY --from=builder /app/dist /usr/share/nginx/html
   COPY nginx-frontend.conf /etc/nginx/conf.d/default.conf
   EXPOSE 80
