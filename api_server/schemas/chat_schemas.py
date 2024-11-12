from pydantic import BaseModel, Field
from datetime import datetime


class BaseMessage(BaseModel):
    content: str = Field(min_length=1)
    owner: int
    chat_id: int
    is_read: bool


class MessageCreateInDB(BaseMessage):
    pass


class MessageFromDB(BaseMessage):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class BaseChat(BaseModel):
    user_1: int
    user_2: int


class ChatFromDB(BaseChat):
    id: int

    class Config:
        from_attributes = True


class ChatCreate(BaseChat):
    pass


class ChatAndRecipient(BaseModel):
    recipient_name: str
    recipient_id: int
    chat_id: int
