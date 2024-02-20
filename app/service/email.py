import os
from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.verify_code import VerifyCodeCheck, VerifyCodeCreate
from crud.crud_verify_code import verify_code
from service.secure import generate_random_num
from dotenv import load_dotenv
from ssl import create_default_context
from email.mime.text import MIMEText
from smtplib import SMTP

load_dotenv()

MAIL_HOST = os.environ.get("MAIL_HOST")
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_PORT = os.environ.get("MAIL_PORT", 587)


async def send_email_message(emails: list[EmailStr], message):
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


async def send_verify_message(email: str, session: AsyncSession):
    email_code = generate_random_num()
    message = f"This your verification code {email_code}"
    message = await send_email_message([email], message=message)
    verifaction_code_obj = VerifyCodeCreate(
        email=email, code=email_code, is_active=True
    )
    return await verify_code.create(db=session, obj_in=verifaction_code_obj)


async def check_code(code: VerifyCodeCheck, session: AsyncSession):
    code_obj = await verify_code.get(db=session, id=code.id)
    if code_obj.is_active:
        return await verify_code.remove(db=session, id=code_obj.id)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid code"
        )
