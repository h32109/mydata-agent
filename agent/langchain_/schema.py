import typing as t
from pydantic import BaseModel, ConfigDict


class LangChainChunkRequest(BaseModel):
    chunk_size: int
    chunk_overlap: int


class LangChainSearchRequest(BaseModel):
    query: str
    k: int = 3


class LangChainSearchResponse(BaseModel):
    documents: t.Any
    model_name: str
    model_config = ConfigDict(protected_namespaces=())


class LangChainVectorStoreRequest(BaseModel):
    model_name: str
    model_config = ConfigDict(protected_namespaces=())
