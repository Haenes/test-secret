import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_USER: str = Field(validation_alias='POSTGRES_USER')
    DB_PASSWORD: str = Field(validation_alias='POSTGRES_PASSWORD')
    DB_HOST: str = Field(validation_alias='POSTGRES_HOST')
    DB_PORT: int = Field(validation_alias='POSTGRES_PORT')
    DB_NAME: str = Field(validation_alias='POSTGRES_DB')

    ENCRYPTION_KEY: str

    REDIS_USER: str
    REDIS_PASSWORD: str
    REDIS_EXPIRE_TIME: int = 300

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.pardir, ".env"),
        env_file_encoding='utf-8'
    )

    def get_db_url(self):
        return (
            f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@'
            f'{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
        )


settings = Settings()
