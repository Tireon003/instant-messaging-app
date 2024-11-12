from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import text, String, ForeignKey
from datetime import datetime as dt
from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .chats import ChatsORM


class MessagesORM(Base):
    """
    Model for table 'messages'

    id: id of unique message
    chat_id: id of chat
    timestamp: timestamp of message
    owner: id of message owner
    content: text of message
    """

    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id"), nullable=False, index=True
    )
    timestamp: Mapped[dt] = mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )
    owner: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    is_read: Mapped[bool] = mapped_column(
        nullable=False, server_default=text("true")
    )

    chat: Mapped["ChatsORM"] = relationship(
        back_populates="history",
        lazy="joined",
    )
