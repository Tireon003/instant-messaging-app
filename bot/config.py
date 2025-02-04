from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str

    DB_NAME: str
    DB_HOST: str
    DB_USER: str
    DB_PORT: str
    DB_PASS: str

    API_HOST: str
    API_PORT: int

    JWT_SECRET: str

    LOG_LEVEL: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
