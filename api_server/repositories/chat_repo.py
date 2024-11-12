from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import aliased

from api_server.schemas import (
    MessageCreateInDB,
    ChatCreate,
    ChatAndRecipient,
)
from api_server.models import MessagesORM, ChatsORM, UsersORM


class ChatRepo:

    def __init__(self, session: AsyncSession) -> None:
        self.__session = session

    async def insert_message(self, message: MessageCreateInDB) -> MessagesORM:
        new_message = MessagesORM(**message.model_dump())
        self.__session.add(new_message)
        await self.__session.flush()
        await self.__session.refresh(new_message)
        await self.__session.commit()
        return new_message

    async def select_messages(self, chat_id: int) -> list[MessagesORM]:
        stmt = (
            select(MessagesORM)
            .filter_by(chat_id=chat_id)
            .order_by(MessagesORM.id)
        )
        result = await self.__session.scalars(stmt)
        messages = [message for message in result.all()]
        return messages

    async def select_chat(self, user_1: int, user_2: int) -> ChatsORM | None:
        stmt = select(ChatsORM).where(
            or_(
                and_(
                    ChatsORM.user_1 == user_1,
                    ChatsORM.user_2 == user_2,
                ),
                and_(
                    ChatsORM.user_1 == user_2,
                    ChatsORM.user_2 == user_1,
                ),
            )
        )
        result = await self.__session.scalars(stmt)
        chat = result.one_or_none()
        return chat

    async def select_chats(self, user_id: int) -> list[ChatAndRecipient]:
        user_1_alias = aliased(UsersORM)
        user_2_alias = aliased(UsersORM)
        stmt = (
            select(
                ChatsORM.id.label("chat_id"),
                user_1_alias.username.label("recipient_name"),
                user_1_alias.id.label("recipient_id"),
            )
            .join(user_1_alias, ChatsORM.user_1 == user_1_alias.id)
            .where(ChatsORM.user_2 == user_id)
            .union_all(
                select(
                    ChatsORM.id.label("chat_id"),
                    user_2_alias.username.label("recipient_name"),
                    user_2_alias.id.label("recipient_id"),
                )
                .join(user_2_alias, ChatsORM.user_2 == user_2_alias.id)
                .where(ChatsORM.user_1 == user_id)
            )
        )
        result = await self.__session.execute(stmt)
        chats = [
            ChatAndRecipient(
                chat_id=row.chat_id,
                recipient_name=row.recipient_name,
                recipient_id=row.recipient_id,
            )
            for row in result.all()
        ]
        return chats

    async def insert_chat(self, chat_schema: ChatCreate) -> ChatsORM:
        new_chat = ChatsORM(**chat_schema.model_dump())
        self.__session.add(new_chat)
        await self.__session.flush()
        await self.__session.refresh(new_chat)
        await self.__session.commit()
        return new_chat

    async def select_messages_by_ids(
        self, messages: Sequence[int]
    ) -> list[MessagesORM]:
        stmt = select(MessagesORM).where(MessagesORM.id.in_(messages))
        result = await self.__session.scalars(stmt)
        return list(result.all())

    async def update_messages(self, messages: Sequence[MessagesORM]) -> None:
        for message in messages:
            message.is_read = True
        await self.__session.commit()
