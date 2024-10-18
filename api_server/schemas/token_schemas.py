from pydantic import BaseModel


class TokenPayload(BaseModel):
    tg_chat_id: int
    sub: int
