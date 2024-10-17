from pydantic import BaseModel, Field


class BaseUser(BaseModel):
    username: str = Field(min_length=6, max_length=20)


class UserCredentials(BaseUser):
    password: str = Field(min_length=8, max_length=50)


class UserLogin(UserCredentials):
    pass


class UserSignup(UserCredentials):
    pass


class UserInsertToDB(BaseUser):
    hashed_password: str
    tg_chat_id: int
