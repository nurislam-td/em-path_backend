from sqlalchemy import insert, update

from app.core.database import engine
from app.models.auth import VerifyCode
from app.service import email, secure
from app.tasks.celery import celery


@celery.task
def deactivate_verify_code(email):
    with engine.begin() as conn:
        table = VerifyCode.__table__
        conn.execute(update(table).values(is_active=False).filter_by(email=email))


@celery.task
def send_verify_message(email_in: str):
    email_code = secure.generate_random_num()
    message = f"This your verification code {email_code}"
    message = email.send_email_message([email_in], message=message)
    with engine.begin() as conn:
        table = VerifyCode.__table__
        conn.execute(update(table).values(is_active=False).filter_by(email=email_in))
        conn.execute(
            insert(table).values(email=email_in, code=email_code, is_active=True)
        )
