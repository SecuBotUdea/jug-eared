from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secubot_url: str
    discord_url: str
    parser_url: str
    mongo_uri: str
    mongo_db_name: str = "secubot"

    class Config:
        env_file = ".env"


settings = Settings()