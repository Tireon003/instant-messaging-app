from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_server.models import UsersORM
from api_server.schemas import UserInsertToDB


class UserRepo:

    def __init__(self, session: AsyncSession) -> None:
        self.__session = session

    async def select_user_by_username(self, username: str) -> UsersORM | None:
        stmt = (
            select(UsersORM)
            .filter_by(username=username)
        )
        result = await self.__session.scalar(stmt)
        return result

    async def insert_user(self, user_record: UserInsertToDB) -> None:
        new_user = UsersORM(**user_record.model_dump())
        self.__session.add(new_user)
        await self.__session.commit()

    async def select_by_tg_chat_id(self, tg_chat_id: int) -> UsersORM | None:
        stmt = (
            select(UsersORM)
            .filter_by(tg_chat_id=tg_chat_id)
        )
        result = await self.__session.scalars(stmt)
        user = result.one_or_none()
        return user

    async def select_user(self, user_id: int) -> UsersORM | None:
        user = await self.__session.get(UsersORM, user_id)
        return user
