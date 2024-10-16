from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .messages import MessagesORM


class ChatsORM(Base):
    """
    #todo дописать доку
    """
    __tablename__ = 'chats'

    id:  Mapped[int] = mapped_column(primary_key=True)
    user_1: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False,
    )
    user_2: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint('user_1', 'user_2', name='unique_users'),
    )

    history: Mapped[list["MessagesORM"]] = relationship(
        back_populates='chat',
        lazy="selectin",
    )
