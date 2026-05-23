// ── Yapılandırma ──────────────────────────────────────────────
const N8N_WEBHOOK = "http://sunucu:5678/webhook/web";
const API_KEY     = "degistir-beni";
const USER_ID     = 1;
const FLUSH_INTERVAL_SEC = 60;

// ── Sosyal / eğlence domain listesi ──────────────────────────
const SOCIAL_DOMAINS = new Set([
  "facebook.com", "twitter.com", "x.com", "instagram.com",
  "tiktok.com", "snapchat.com", "linkedin.com", "reddit.com",
]);
const ENTERTAINMENT_DOMAINS = new Set([
  "youtube.com", "netflix.com", "twitch.tv", "spotify.com",
  "primevideo.com", "disneyplus.com",
]);
const NEWS_DOMAINS = new Set([
  "cnn.com", "bbc.com", "ntvmsnbc.com", "hurriyet.com.tr",
  "milliyet.com.tr", "sabah.com.tr",
]);

function categorize(domain) {
  const d = domain.replace(/^www\./, "");
  if (SOCIAL_DOMAINS.has(d))       return "social";
  if (ENTERTAINMENT_DOMAINS.has(d)) return "entertainment";
  if (NEWS_DOMAINS.has(d))          return "news";
  return "other";
}

// ── Oturum durumu ─────────────────────────────────────────────
let activeTabId   = null;
let activeUrl     = null;
let activeDomain  = null;
let activeTitle   = null;
let sessionStart  = null;
const pending     = [];   // { domain, url, title, category, duration_sec, visited_at }

function getDomain(url) {
  try { return new URL(url).hostname; } catch { return ""; }
}

function flushCurrent(now = Date.now()) {
  if (!activeUrl || !sessionStart) return;
  const duration = Math.round((now - sessionStart) / 1000);
  if (duration < 2) return;
  pending.push({
    domain:       activeDomain,
    url:          activeUrl,
    page_title:   activeTitle || "",
    category:     categorize(activeDomain),
    duration_sec: duration,
    visited_at:   new Date(sessionStart).toISOString(),
  });
}

function startSession(url, title, tabId) {
  activeUrl    = url;
  activeDomain = getDomain(url);
  activeTitle  = title;
  activeTabId  = tabId;
  sessionStart = Date.now();
}

// ── Tab olayları ──────────────────────────────────────────────
chrome.tabs.onActivated.addListener(async ({ tabId }) => {
  flushCurrent();
  try {
    const tab = await chrome.tabs.get(tabId);
    if (tab.url && !tab.url.startsWith("chrome://")) {
      startSession(tab.url, tab.title, tabId);
    }
  } catch {}
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (tabId !== activeTabId) return;
  if (changeInfo.status === "complete" && tab.url) {
    flushCurrent();
    startSession(tab.url, tab.title, tabId);
  }
});

chrome.tabs.onRemoved.addListener((tabId) => {
  if (tabId === activeTabId) {
    flushCurrent();
    activeUrl = null;
    sessionStart = null;
  }
});

// ── Periyodik n8n gönderimi ───────────────────────────────────
chrome.alarms.create("flush", { periodInMinutes: FLUSH_INTERVAL_SEC / 60 });

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name !== "flush") return;
  flushCurrent();
  if (!pending.length) return;
  const batch = pending.splice(0);
  try {
    await fetch(N8N_WEBHOOK, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-Key": API_KEY },
      body: JSON.stringify({ user_id: USER_ID, events: batch }),
    });
  } catch (err) {
    // Gönderim başarısız → geri koy
    pending.unshift(...batch);
    console.warn("[Takip] Gönderim hatası:", err.message);
  }
});
