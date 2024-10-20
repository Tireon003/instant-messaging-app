from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BIGINT

from .base import Base


class UsersORM(Base):
    """
    Model of table "users"

    id: unique user id
    username: unique username
    hashed_password: hashed password
    tg_chat_id: unique id of the chat between the bot and the user for sending notifications
    """

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(25), nullable=False, unique=True)
    hashed_password: Mapped[str]
    tg_chat_id: Mapped[int] = mapped_column(BIGINT, nullable=False, unique=True)

