from datetime import UTC, datetime, timedelta
from typing import cast

from sqlalchemy import TableClause, delete, insert, update

from app.core.database import engine
from app.core.settings import settings
from app.interfaces.task_manager import ITaskManager
from app.models.auth import VerifyCode
from app.service import mail_send, secure
from app.tasks.celery_app import celery_app


@celery_app.task()
def deactivate_verify_code(email_in: str):
    with engine.begin() as conn:
        table = cast(TableClause, VerifyCode.__table__)
        conn.execute(update(table).values(is_active=False).filter_by(email=email_in))


@celery_app.task()
def send_verify_message(email_in: str):
    email_code = secure.generate_random_num()
    message = f"This your verification code {email_code}"
    message = mail_send.send_email_message([email_in], message=message)
    with engine.begin() as conn:
        table = cast(TableClause, VerifyCode.__table__)
        conn.execute(update(table).values(is_active=False).filter_by(email=email_in))
        conn.execute(
            insert(table).values(email=email_in, code=email_code, is_active=True)
        )


@celery_app.task(name="clean_verify_code_table")
def clean_verify_code_table():
    with engine.begin() as conn:
        table = cast(TableClause, VerifyCode.__table__)
        time_filter = datetime.now(UTC) - timedelta(
            minutes=settings.auth_config.verification_code_expire
        )
        conn.execute(delete(table).where(table.c.created_at < time_filter))


class CeleryTaskManager(ITaskManager):
    def send_verify_message(self, email_in: str):
        send_verify_message.delay(email_in)

    def deactivate_verify_code(self, email_in: str):
        deactivate_verify_code.delay(email_in)

    def clean_verify_code_table(self):
        clean_verify_code_table.delay()
