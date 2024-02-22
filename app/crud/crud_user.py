from typing import Any, Dict, Optional, Union
from sqlalchemy import select, Result

from sqlalchemy.ext.asyncio import AsyncSession

from service.secure import get_password_hash, verify_password
from crud.base import CRUDBase
from models.auth import User
from schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        user_res: Result = await db.execute(select(User).where(User.email == email))
        return user_res.scalars().one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = User(**obj_in.model_dump())
        db_obj.password = get_password_hash(db_obj.password)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["password"] = hashed_password
        return await super().update(db, db_obj=db_obj, obj_in=update_data)


user = CRUDUser(User)
