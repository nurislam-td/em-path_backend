import os
from datetime import UTC, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP
from ssl import create_default_context

from dotenv import load_dotenv
from pydantic import EmailStr

from app.core.exceptions import IncorrectVerificationCode
from app.core.settings import settings
from app.interfaces.task_manager import ITaskManager
from app.interfaces.unit_of_work import IUnitOfWork
from app.schemas.verify_code import VerifyCodeCheck, VerifyCodeDTO
from app.utils import render

load_dotenv()

MAIL_HOST = os.environ.get("MAIL_HOST")
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_PORT = os.environ.get("MAIL_PORT", 587)


def send_email_message(emails: list[EmailStr], message) -> MIMEText | dict:
    # TODO refactor this
    body = message
    message = MIMEText(body)
    message["From"] = MAIL_USERNAME
    message["To"] = ",".join(emails)
    message["Subject"] = "Empath notification"

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


def send_email_template(
    emails: list[EmailStr], template_name: str, **data
) -> str | dict:
    template = render.render_template(template_name, **data)
    message = MIMEMultipart("alternative")
    message["From"] = MAIL_USERNAME
    message["To"] = ",".join(emails)
    message["Subject"] = "Empath notification"
    message.attach(MIMEText(template, "html"))
    ctx = create_default_context()
    try:
        with SMTP(MAIL_HOST, MAIL_PORT) as server:
            server.ehlo()
            server.starttls(context=ctx)
            server.ehlo()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(
                from_addr=message["From"],
                to_addrs=message["To"],
                msg=message.as_string(),
            )
            server.quit()
        return message.as_string()
    except Exception as e:
        return {"error": e}


async def check_code(
    code: VerifyCodeCheck, uow: IUnitOfWork, task_manager: ITaskManager
) -> int:
    async with uow:
        code_dto: VerifyCodeDTO = await uow.verify_code.get_last_active_by_email(
            email_in=code.email
        )

        if code_dto and code_dto.is_active:
            expire_date = datetime.now(UTC) - timedelta(
                minutes=settings.auth_config.verification_code_expire
            )
            if (
                code_dto.created_at.replace(tzinfo=UTC) > expire_date
                and code.code == code_dto.code
            ):
                task_manager.deactivate_verify_code(email_in=code_dto.email)
                return 200

        raise IncorrectVerificationCode
