import os

from pydantic_settings import BaseSettings, SettingsConfigDict

from agent.enums import Environment, Device
from agent.utils import get_path_from_root


class Setting(BaseSettings):
    API_PREFIX: str = "/api/v1"

    APP_VERSION: str = "0.0.1"
    ENV: Environment = Environment.DEV

    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8000

    LOGGING_LEVEL: str = "INFO"

    # chatgpt
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    TEMPERATURE: float | None = 0

    # langchain
    DEFAULT_EMBEDDING_MODEL: str = "upskyy/kf-deberta-multitask"
    EMBEDDING_DEVICE: Device = Device.CPU
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    REFRESH_VECTOR_STORE: bool = False

    @property
    def is_dev(self) -> bool:
        return self.ENV == Environment.DEV

    model_config = SettingsConfigDict(
        env_file=get_path_from_root(f'config/{os.getenv("PROFILE", "dev")}.env'),
        env_file_encoding='utf-8',
        case_sensitive=False
    )


settings = Setting()
