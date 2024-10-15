from pydantic import BaseModel, Field


class BaseUser(BaseModel):
    username: str = Field(min_length=6, max_length=20)


class UserLogin(BaseUser):
    password: str = Field(min_length=8, max_length=50)
