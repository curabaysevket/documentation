.. _desktime-frontend-implementation:

============================
Frontend Uygulama Detayları
============================

Proje Yapısı
-------------

.. code-block:: text

   frontend/
   ├── public/
   │   └── index.html
   ├── src/
   │   ├── pages/
   │   │   ├── Dashboard.tsx
   │   │   ├── Reports.tsx
   │   │   ├── Screenshots.tsx
   │   │   ├── Projects.tsx
   │   │   └── TeamAdmin.tsx
   │   ├── components/
   │   │   ├── ActivityTimeline.tsx   # Saatlik aktivite şeridi
   │   │   ├── ProductivityPieChart.tsx
   │   │   ├── AppUsageTable.tsx
   │   │   ├── ScreenshotGrid.tsx
   │   │   ├── TeamLiveView.tsx       # Gerçek zamanlı ekip durumu
   │   │   └── Layout.tsx
   │   ├── hooks/
   │   │   ├── useRealtimeActivity.ts # WebSocket hook
   │   │   └── useAuth.ts
   │   ├── api/
   │   │   ├── client.ts             # Axios instance + JWT interceptor
   │   │   ├── dashboard.ts
   │   │   ├── reports.ts
   │   │   └── screenshots.ts
   │   ├── store/
   │   │   └── authStore.ts          # Zustand: oturum state
   │   ├── types/
   │   │   └── index.ts              # TypeScript tip tanımları
   │   ├── App.tsx
   │   └── main.tsx
   ├── package.json
   └── tailwind.config.ts

API İstemcisi (Axios + JWT Interceptor)
-----------------------------------------

.. code-block:: typescript

   // api/client.ts
   import axios from 'axios';

   const api = axios.create({
     baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
   });

   api.interceptors.request.use((config) => {
     const token = localStorage.getItem('access_token');
     if (token) config.headers.Authorization = `Bearer ${token}`;
     return config;
   });

   api.interceptors.response.use(
     (res) => res,
     async (err) => {
       if (err.response?.status === 401) {
         const refresh = localStorage.getItem('refresh_token');
         const { data } = await axios.post('/api/v1/auth/refresh',
                                           { token: refresh });
         localStorage.setItem('access_token', data.access_token);
         return api.request(err.config);
       }
       return Promise.reject(err);
     }
   );

   export default api;

Gerçek Zamanlı WebSocket Hook
------------------------------

.. code-block:: typescript

   // hooks/useRealtimeActivity.ts
   import { useEffect, useCallback } from 'react';
   import { useQueryClient } from '@tanstack/react-query';

   export function useRealtimeActivity() {
     const qc = useQueryClient();
     const token = localStorage.getItem('access_token');

     const connect = useCallback(() => {
       const ws = new WebSocket(
         `${import.meta.env.VITE_WS_URL}/ws/realtime?token=${token}`
       );

       ws.onmessage = (event) => {
         const data = JSON.parse(event.data);
         // Gelen aktivite güncellemesinde React Query cache'i invalidate et
         qc.invalidateQueries({ queryKey: ['dashboard', 'summary'] });
         qc.invalidateQueries({ queryKey: ['dashboard', 'timeline'] });
       };

       ws.onclose = () => {
         setTimeout(connect, 3000);  // 3 saniye sonra yeniden bağlan
       };

       return ws;
     }, [token, qc]);

     useEffect(() => {
       const ws = connect();
       return () => ws.close();
     }, [connect]);
   }

Aktivite Zaman Çizelgesi Bileşeni
-----------------------------------

.. code-block:: typescript

   // components/ActivityTimeline.tsx
   import { useQuery } from '@tanstack/react-query';
   import api from '../api/client';

   const CATEGORY_COLORS = {
     productive:    '#22c55e',  // yeşil
     unproductive:  '#ef4444',  // kırmızı
     neutral:       '#94a3b8',  // gri
     idle:          '#f1f5f9',  // açık gri
   };

   export function ActivityTimeline({ userId, date }: Props) {
     const { data } = useQuery({
       queryKey: ['dashboard', 'timeline', userId, date],
       queryFn: () => api.get(`/api/v1/dashboard/timeline?user_id=${userId}&date=${date}`)
                        .then(r => r.data),
       refetchInterval: 60_000,
     });

     // Her saat bloğunu 60px genişlik ile çiz
     return (
       <div className="flex gap-0.5 h-12 rounded overflow-hidden">
         {data?.hours.map((hour: HourBlock) => (
           <div
             key={hour.hour}
             style={{
               backgroundColor: CATEGORY_COLORS[hour.dominant_category],
               width: `${(hour.active_minutes / 60) * 100}%`,
             }}
             title={`${hour.hour}:00 — ${hour.dominant_category} (${hour.active_minutes}dk)`}
           />
         ))}
       </div>
     );
   }

Dashboard Sayfası
------------------

.. code-block:: typescript

   // pages/Dashboard.tsx
   import { ActivityTimeline } from '../components/ActivityTimeline';
   import { ProductivityPieChart } from '../components/ProductivityPieChart';
   import { TeamLiveView } from '../components/TeamLiveView';
   import { useRealtimeActivity } from '../hooks/useRealtimeActivity';
   import { useQuery } from '@tanstack/react-query';
   import api from '../api/client';
   import { format } from 'date-fns';

   export function Dashboard() {
     useRealtimeActivity();  // WebSocket bağlantısını başlat
     const today = format(new Date(), 'yyyy-MM-dd');

     const { data: summary } = useQuery({
       queryKey: ['dashboard', 'summary'],
       queryFn: () => api.get('/api/v1/dashboard/summary').then(r => r.data),
       refetchInterval: 30_000,
     });

     return (
       <div className="p-6 space-y-6">
         <h1 className="text-2xl font-bold">Bugün</h1>

         {/* Üretkenlik skoru */}
         <div className="grid grid-cols-3 gap-4">
           <StatCard label="Üretken" value={summary?.productive_hours} unit="saat" color="green" />
           <StatCard label="Toplam Aktif" value={summary?.active_hours} unit="saat" color="blue" />
           <StatCard label="Skor" value={summary?.productivity_score} unit="%" color="purple" />
         </div>

         {/* Saatlik zaman çizelgesi */}
         <section>
           <h2 className="font-semibold mb-2">Aktivite Çizelgesi</h2>
           <ActivityTimeline userId="me" date={today} />
         </section>

         {/* Uygulama dağılımı */}
         <section className="grid grid-cols-2 gap-6">
           <ProductivityPieChart date={today} />
           <AppUsageTable date={today} />
         </section>

         {/* Ekip canlı görünümü (sadece yöneticiler) */}
         <TeamLiveView />
       </div>
     );
   }

Kurulum
--------

.. code-block:: bash

   cd frontend
   npm create vite@latest . -- --template react-ts
   npm install
   npm install @tanstack/react-query axios recharts zustand react-router-dom date-fns
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p

   # Geliştirme sunucusu
   npm run dev

   # Production build
   npm run build
