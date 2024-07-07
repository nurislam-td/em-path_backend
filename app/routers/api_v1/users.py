from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.dependencies.common import get_file_client, get_uow
from app.schemas.token import TokenOut
from app.schemas.user import Gender, UserCreate, UserDTO, UserUpdate
from app.service import user
from app.service.abstract.unit_of_work import UnitOfWork

from ...dependencies.auth import get_current_user
from ...service.abstract.file_client import FileClient

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate, uow: UnitOfWork = Depends(get_uow)
) -> TokenOut:
    user_data = await user.create_user(user_data, uow=uow)
    tokens = await user.login(user_data=user_data, uow=uow)
    return tokens


@router.patch("", status_code=status.HTTP_200_OK)
async def update_user(
    email: str = Form(None),
    nickname: str = Form(None),
    gender: Gender = Form(None),
    name: str = Form(None),
    lastname: str = Form(None),
    patronymic: str = Form(None),
    date_birth: date = Form(None),
    image: UploadFile = File(None),
    uow: UnitOfWork = Depends(get_uow),
    file_client: FileClient = Depends(get_file_client),
    user_data: UserDTO = Depends(get_current_user),
) -> UserDTO:
    return await user.update_user(
        user_id=user_data.id,
        update_data=UserUpdate(
            email=email,
            nickname=nickname,
            gender=gender,
            name=name,
            lastname=lastname,
            patronymic=patronymic,
            date_birth=date_birth,
            image=image,
        ),
        uow=uow,
        file_client=file_client,
    )


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: UUID, uow: UnitOfWork = Depends(get_uow)) -> None:
    await user.delete_user(user_id=user_id, uow=uow)


@router.get("", status_code=status.HTTP_200_OK)
async def get_users(uow: UnitOfWork = Depends(get_uow)) -> list[UserDTO]:
    return await user.get_all(uow=uow)


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_me(user_data: UserDTO = Depends(get_current_user)) -> UserDTO:
    return user_data
