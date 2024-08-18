from typing import Dict

from pydantic import BaseModel, Field

from agent.enums import ChainType, SearchType
from agent.context.langchain_ctx import LangchainParameterBase


class RAGResponse(BaseModel):
    msg: str
    details: Dict = Field(default_factory=dict)


class RAGRequest(LangchainParameterBase):
    query: str
    chain_type: ChainType = Field(default=ChainType.MAP_REDUCE)
    search_type: SearchType = Field(default=SearchType.SIMILARITY)


class RAGDocument(BaseModel):
    metadata: Dict
    page_content: str
