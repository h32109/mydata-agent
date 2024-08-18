import typing as t
from datetime import timedelta

from cachetools import TTLCache

from agent.context.langchain_ctx import Retriever
from agent.context.langchain_ctx.plugins.retriever import TokenManagedMemory
from agent.service import Service, ServiceBase
from agent.rag.schema import RAGDocument
from agent.globals import lc


class RAGServiceBase(ServiceBase):
    settings: t.Any
    memories_cache: TTLCache = TTLCache(maxsize=1024, ttl=timedelta(hours=1).total_seconds())

    def configuration(self, settings: t.Any) -> None:
        self.settings = settings

    def get_cache(self, key: str) -> t.Any:
        return self.memories_cache[key]


class RAGService(RAGServiceBase):
    @staticmethod
    def _wrap_result(result: dict, embedding_model_name: str, llm_model_name: str) -> dict:
        source_documents = result.pop("source_documents", [])
        return {
            **result,
            "source_documents": [
                RAGDocument(**dict(s)).model_dump() for s in source_documents
            ],
            "model": llm_model_name,
            "embedding_model": embedding_model_name
        }

    def _get_or_create_memory(self, conversation_id: str) -> TokenManagedMemory:
        return self.memories_cache.setdefault(
            conversation_id,
            TokenManagedMemory(memory_key=conversation_id, return_messages=True)
        )

    async def retrieve(self,
                       query: str,
                       chain_type: str,
                       search_type: str,
                       conversation_id: str,
                       retriever: str | None = None) -> dict:
        memory = self._get_or_create_memory(conversation_id)
        prod = lc.get_prod(retriever=retriever)
        result = await prod(Retriever, memory=memory).retrieve(query, chain_type, search_type)
        embedding_model_name = prod.get_embedding_model_name()
        llm_model_name = prod.get_llm_model_name()

        return self._wrap_result(result, embedding_model_name, llm_model_name)


rag_service = Service.add_service(RAGService)
