from fastapi import APIRouter, Depends, status
from pydantic import EmailStr
from schemas.token import TokenOut
from config.database import db
from auth import User
from schemas.user import AuthUser, UserCreate, UserInDbBase
from schemas.verify_code import VerifyOut, VerifyCodeCheck
from service import user, email
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserInDbBase)
async def register_user(
    user_data: UserCreate,
    session=Depends(db.scoped_session_dependency),
) -> dict[str, str]:
    user_obj: User = await user.create_user(user_data, session=session)
    return user_obj


@router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenOut)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session=Depends(db.scoped_session_dependency),
):
    auth_data = AuthUser(email=form_data.username, password=form_data.password)
    return await user.login(auth_data=auth_data, session=session)


@router.post("/users/email/send_code")
async def send_verify_message(
    email_in: EmailStr, session=Depends(db.scoped_session_dependency)
):
    verifyCode = await email.send_verify_message(email=email_in, session=session)
    return VerifyOut(id=verifyCode.id, email=verifyCode.email)


@router.post("/users/email/verify")
async def verify_code(
    code: VerifyCodeCheck, session=Depends(db.scoped_session_dependency)
):
    code_obj = await email.check_code(code, session)
    return {"status": 200 if code_obj else 400}


@router.post("/users/token/refresh")
async def refresh_token(
    refresh_token: str, session=Depends(db.scoped_session_dependency)
):
    pass
