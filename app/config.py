from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secubot_url: str
    discord_url: str

    class Config:
        env_file = ".env"


settings = Settings()