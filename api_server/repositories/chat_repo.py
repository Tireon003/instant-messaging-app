from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api_server.schemas import MessageCreateInDB
from api_server.models import MessagesORM


class ChatRepo:

    def __init__(self, session: AsyncSession) -> None:
        self.__session = session

    async def insert_message(self, message: MessageCreateInDB) -> None:
        new_message = MessagesORM(**message.model_dump())
        self.__session.add(new_message)
        await self.__session.commit()

    async def select_messages(self, chat_id: int) -> list[MessagesORM] | None:
        stmt = (
            select(MessagesORM)
            .filter_by(chat_id=chat_id)
            .order_by(MessagesORM.id)
        )
        result = await self.__session.scalars(stmt)
        messages = [message for message in result.all()]
        return messages
