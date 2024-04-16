import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from smtplib import SMTP
from ssl import create_default_context

from dotenv import load_dotenv
from pydantic import EmailStr

from app.core.database import IUnitOfWork
from app.core.exceptions import IncorrectVerificationCode
from app.core.settings import settings
from app.schemas.verify_code import VerifyCodeCheck, VerifyOut
from app.service.secure import generate_random_num

load_dotenv()

MAIL_HOST = os.environ.get("MAIL_HOST")
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_PORT = os.environ.get("MAIL_PORT", 587)


def send_email_message(emails: list[EmailStr], message) -> MIMEText:
    body = message
    message = MIMEText(body)
    message["From"] = MAIL_USERNAME
    message["To"] = ",".join(emails)
    message["Subject"] = "Empath verification code"

    ctx = create_default_context()
    try:
        with SMTP(MAIL_HOST, MAIL_PORT) as server:
            server.ehlo()
            server.starttls(context=ctx)
            server.ehlo()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(message)
            server.quit()
        return message
    except Exception as e:
        return {"error": e}


async def send_verify_message(email: str, uow: IUnitOfWork) -> VerifyOut:
    email_code = generate_random_num()
    message = f"This your verification code {email_code}"
    message = send_email_message([email], message=message)
    async with uow:
        # TODO(fix) make it via celery or bacground task
        await uow.verify_code.update(
            values={"is_active": False}, filters={"email": email}
        )
        # end_todo
        verify_code_dict = await uow.verify_code.create(
            values={
                "email": email,
                "code": email_code,
                "is_active": True,
            }
        )
        await uow.commit()
        return VerifyOut(**verify_code_dict)


async def check_code(code: VerifyCodeCheck, uow: IUnitOfWork) -> None:
    async with uow:
        code_dict = await uow.verify_code.get_last_active_by_email(email_in=code.email)

        if code_dict and code_dict["is_active"]:
            expire_date = datetime.now() - timedelta(
                minutes=settings.auth_config.verification_code_expire
            )
            # TODO(fix) make it via celery or bacground task
            await uow.verify_code.update(
                values={"is_active": False}, filters={"email": code_dict["email"]}
            )
            await uow.commit()
            # end todo
            if code_dict["created_at"] > expire_date and code.code == code_dict["code"]:
                return 200

        raise IncorrectVerificationCode


# TODO(implement) delete all inactive verify message on 00:00 utc-0+
