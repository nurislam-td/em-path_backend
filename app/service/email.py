import os
from typing import Any
from fastapi import HTTPException, status
from pydantic import EmailStr
from schemas.verify_code import VerifyCodeCheck, VerifyOut
from service.secure import generate_random_num
from dotenv import load_dotenv
from ssl import create_default_context
from email.mime.text import MIMEText
from smtplib import SMTP
from config.database import IUnitOfWork


load_dotenv()

MAIL_HOST = os.environ.get("MAIL_HOST")
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_PORT = os.environ.get("MAIL_PORT", 587)


async def send_email_message(emails: list[EmailStr], message) -> MIMEText:
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
    message = await send_email_message([email], message=message)
    async with uow:
        verify_code_dict = await uow.verify_code.create(
            values={
                "email": email,
                "code": email_code,
                "is_active": True,
            }
        )
        await uow.commit()
        return VerifyOut(id=verify_code_dict["id"], email=verify_code_dict["email"])


async def check_code(code: VerifyCodeCheck, uow: IUnitOfWork) -> None:
    async with uow:
        code_dict = await uow.verify_code.get(code.id)
        if code_dict["is_active"]:
            return await uow.verify_code.delete(filters={"id": code_dict["id"]})
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="invalid code"
            )
