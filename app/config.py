from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_url: str | None = Field(
        default=None, title="MongoDB URL", description="MongoDB URL with credentials"
    )
    mongodb_name: str | None = Field(
        default=None,
        title="MongoDB Database Name",
        description="MongoDB Database Name to connect to",
    )

    class Config:
        env_file = ".env"


settings = Settings()
