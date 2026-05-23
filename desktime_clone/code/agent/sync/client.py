import httpx
import config


def _post(endpoint: str, payload: dict) -> bool:
    url = f"{config.N8N_BASE_URL}/webhook/{endpoint}"
    try:
        r = httpx.post(url, json=payload, headers=config.HEADERS, timeout=10)
        return r.is_success
    except Exception as exc:
        print(f"[Sync] {endpoint} gönderim hatası: {exc}")
        return False


def send_activity_batch(events: list[dict]) -> bool:
    return _post("activity", {
        "user_id": config.USER_ID,
        "events":  events,
    })


def send_email_stats(stats: dict) -> bool:
    return _post("email", {
        "user_id": config.USER_ID,
        **stats,
    })


def send_file_event(file_path: str, event_type: str, app_name: str = "") -> bool:
    return _post("file", {
        "user_id":    config.USER_ID,
        "file_path":  file_path,
        "event_type": event_type,
        "app_name":   app_name,
    })


def send_phone_log(duration_sec: int, direction: str, platform: str = "android") -> bool:
    return _post("phone", {
        "user_id":      config.USER_ID,
        "duration_sec": duration_sec,
        "direction":    direction,
        "platform":     platform,
    })
