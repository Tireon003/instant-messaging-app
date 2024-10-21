from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BIGINT

from .base import Base


class UsersORM(Base):
    """
    Model of table 'users'

    id: id of the user
    username: user's username
    hashed_password: user's hashed password
    tg_chat_id: id if chat with notification telegram bot
    """

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(25), nullable=False, unique=True)
    hashed_password: Mapped[str]
    tg_chat_id: Mapped[int] = mapped_column(BIGINT, nullable=False, unique=True)

