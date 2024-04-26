from celery import Celery

from app.core.settings import settings

celery = Celery("tasks", broker=settings.redis.url, include=["app.tasks.tasks"])
