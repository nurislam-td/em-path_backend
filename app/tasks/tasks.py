from datetime import UTC, datetime, timedelta
from typing import cast

from celery import shared_task
from sqlalchemy import TableClause, delete, insert, update

from app.core.database import engine
from app.core.settings import settings
from app.models.auth import VerifyCode
from app.service import email, secure


@shared_task
def deactivate_verify_code(email_in: str):
    with engine.begin() as conn:
        table = cast(TableClause, VerifyCode.__table__)
        conn.execute(update(table).values(is_active=False).filter_by(email=email_in))


@shared_task
def send_verify_message(email_in: str):
    email_code = secure.generate_random_num()
    message = f"This your verification code {email_code}"
    message = email.send_email_message([email_in], message=message)
    with engine.begin() as conn:
        table = cast(TableClause, VerifyCode.__table__)
        conn.execute(update(table).values(is_active=False).filter_by(email=email_in))
        conn.execute(
            insert(table).values(email=email_in, code=email_code, is_active=True)
        )


@shared_task(name="clean_verify_code_table")
def clean_verify_code_table():
    with engine.begin() as conn:
        table = cast(TableClause, VerifyCode.__table__)
        time_filter = datetime.now(UTC) - timedelta(
            minutes=settings.auth_config.verification_code_expire
        )
        conn.execute(delete(table).where(table.c.created_at < time_filter))
