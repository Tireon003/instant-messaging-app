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

    @property
    def db_url(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

    @property
    def redis_url(self):
        return "redis://redis_cache:6379"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
