from pydantic import BaseModel, Field
from datetime import datetime


class BaseMessage(BaseModel):
    content: str = Field(min_length=1)
    owner: int
    chat_id: int


class MessageCreateInDB(BaseMessage):
    pass


class MessageFromDB(BaseMessage):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class MessageFromDBIncludeRecipient(MessageFromDB):
    recipient: str
