from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import text, Text, ForeignKey
from datetime import datetime as dt
from typing import TYPE_CHECKING

from .base import Base
if TYPE_CHECKING:
    from .chats import ChatsORM


class MessagesORM(Base):
    """
    Model of table "messages"

    id: unique message number
    chat_id: id of chat
    timestamp: timestamp of message
    owner: id of user who sent a message
    content: user message content
    """
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id"),
        nullable=False,
        index=True
    )
    timestamp: Mapped[dt] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    owner: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    chat: Mapped["ChatsORM"] = relationship(
        back_populates="history",
        lazy="joined",
    )
