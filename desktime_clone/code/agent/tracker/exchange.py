from datetime import datetime, timedelta
import config


def fetch_email_stats() -> dict:
    """EWS üzerinden bugünkü mail istatistiklerini döndürür."""
    try:
        from exchangelib import Credentials, Account, DELEGATE, Q
        from exchangelib.protocol import BaseProtocol
        import urllib3
        urllib3.disable_warnings()

        creds   = Credentials(config.EXCHANGE_USER, config.EXCHANGE_PASSWORD)
        account = Account(
            config.EXCHANGE_USER,
            credentials=creds,
            autodiscover=False,
            access_type=DELEGATE,
            primary_smtp_address=config.EXCHANGE_USER,
        )

        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end   = today_start + timedelta(days=1)

        inbox   = account.inbox
        sent    = account.sent

        received_today = inbox.filter(
            datetime_received__gte=today_start,
            datetime_received__lt=today_end,
        ).count()

        sent_today = sent.filter(
            datetime_sent__gte=today_start,
            datetime_sent__lt=today_end,
        ).count()

        read_today = inbox.filter(
            datetime_received__gte=today_start,
            datetime_received__lt=today_end,
            is_read=True,
        ).count()

        return {
            "received_count": received_today,
            "sent_count":     sent_today,
            "read_count":     read_today,
        }
    except Exception as exc:
        print(f"[Exchange] Hata: {exc}")
        return {"received_count": 0, "sent_count": 0, "read_count": 0}
