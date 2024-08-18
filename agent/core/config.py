import os
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from agent.enums import Environment, Device
from agent.utils import get_path_from_root
from agent.context.langchain_ctx import (
    EmbeddingModelLiteral,
    LLMModelLiteral,
    LoaderLiteral,
    SplitterLiteral,
    RetrieverLiteral
)


class Setting(BaseSettings):
    # API 설정
    API_PREFIX: str = "/api/v1"
    APP_VERSION: str = "0.0.1"
    ENV: Environment = Environment.DEV

    # 서버 설정
    UVICORN_HOST: str = "0.0.0.0"
    UVICORN_PORT: int = 8000

    # 로깅 설정
    LOGGING_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # OpenAI 설정
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    TEMPERATURE: float | None = Field(0, ge=0, le=1)

    # Langchain 설정
    EMBEDDING_DEVICE: Device = Device.CPU

    # Unstructured API 설정
    UNSTRUCTURED_API_KEY: str

    # 도메인 및 기본 설정
    DOMAIN: str = "mydata"
    DEFAULT_DATABASE: str = "chroma"
    DEFAULT_EMBEDDING_MODEL: EmbeddingModelLiteral = "openai"
    DEFAULT_LLM_MODEL: LLMModelLiteral = "openai"
    DEFAULT_LOADER: LoaderLiteral = "unstructured_loader"
    DEFAULT_SPLITTER: SplitterLiteral = "recursive_character_spliter"
    DEFAULT_RETRIEVER: RetrieverLiteral = "multiquery_retriever"
    DEFAULT_CHUNK_SIZE: int = Field(1000, gt=0)
    DEFAULT_CHUNK_OVERLAP: int = Field(200, ge=0)

    @property
    def is_dev(self) -> bool:
        return self.ENV == Environment.DEV

    model_config = SettingsConfigDict(
        env_file=get_path_from_root(f'config/{os.getenv("PROFILE", "dev")}.env'),
        env_file_encoding='utf-8',
        case_sensitive=False
    )


settings = Setting()
