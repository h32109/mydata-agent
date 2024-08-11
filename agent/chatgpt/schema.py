from agent.enums import RetrieverType, ChainType, SearchType

from pydantic import BaseModel


class ChatGPTResponse(BaseModel):
    msg: str
    details: dict | None = {}


class ChatGPTReadRequest(BaseModel):
    query: str
    chain_type: ChainType | None = ChainType.MAP_REDUCE
    retriever_type: RetrieverType | None = RetrieverType.MULTI_QUERY
    search_type: SearchType | None = SearchType.SIMILARITY


class ChatGPTDocument(BaseModel):
    metadata: dict
    page_content: str
