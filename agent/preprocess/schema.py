from pydantic import BaseModel, Field

from agent.context.langchain_ctx import LangchainParameterBase


class LoadRequest(LangchainParameterBase):
    ...


class ChunkRequest(LangchainParameterBase):
    chunk_size: int = Field(default=1000, gt=0)
    chunk_overlap: int = Field(default=200, gt=0)


class SearchRequest(BaseModel):
    query: str
    k: int = Field(default=3)


class VectorStoreRequest(LangchainParameterBase):
    ...