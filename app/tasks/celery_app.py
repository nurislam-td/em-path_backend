from celery import Celery
from celery.schedules import crontab

from app.common.settings import settings

celery_app = Celery("tasks", broker=settings.redis.url, include=["app.tasks.tasks"])

celery_app.conf.beat_schedule = {
    "run-every-midnight": {
        "task": "clean_verify_code_table",
        "schedule": crontab(minute="0", hour="0"),  # run every 00:00 UTC+0
    }
}
