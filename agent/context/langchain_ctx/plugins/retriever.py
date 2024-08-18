__all__ = ('Retriever',)

import tiktoken
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.retrievers import (
    MultiQueryRetriever,
    EnsembleRetriever
)

from langchain_community.retrievers import BM25Retriever
from pydantic import Field

from .base import PluginBase


class TokenManagedMemory(ConversationBufferMemory):
    max_token_limit: int = Field(default=3000)
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def save_context(self, inputs: dict, outputs: dict) -> None:
        super().save_context(inputs, outputs)
        self._trim_history()

    def _trim_history(self) -> None:
        current_tokens = sum(len(self.encoding.encode(msg.content)) for msg in self.chat_memory.messages)

        while current_tokens > self.max_token_limit and len(self.chat_memory.messages) > 1:
            removed_message = self.chat_memory.messages.pop(0)
            current_tokens -= len(self.encoding.encode(removed_message.content))


class Retriever(PluginBase):

    def __init__(
            self,
            prod,
            memory,
            *args,
            **kwargs
    ):
        super(Retriever, self).__init__(prod, *args, **kwargs)
        self.memory = memory

    async def _retrieve(self,
                        vs_retriever,
                        retriever,
                        llm_model,
                        query,
                        chain_type
                        ):

        if retriever == MultiQueryRetriever:
            retriever: MultiQueryRetriever = retriever.from_llm(
                retriever=vs_retriever,
                llm=llm_model
            )

        elif retriever == EnsembleRetriever:
            docs = await self.prod.get_docs()
            bm25_retriever = BM25Retriever.from_documents(docs)
            bm25_retriever.k = 3
            retriever: EnsembleRetriever = retriever(
                retrievers=[bm25_retriever, vs_retriever], weights=[0.5, 0.5]
            )

        qa = ConversationalRetrievalChain.from_llm(
            llm=llm_model,
            retriever=retriever or vs_retriever,
            chain_type=chain_type,
            return_source_documents=True,
        )

        result = qa.invoke({"question": query, "chat_history": self.memory.chat_memory.messages})

        return {"answer": result['answer'], "source_documents": result['source_documents']}

    async def retrieve(self, query, chain_type, search_type):
        vs_retriever = self.prod.get_vector_store_retriever(search_type)
        retriever = self.prod.get_retriever()
        llm_model = self.prod.get_llm_model()

        self.memory.chat_memory.add_user_message(query)

        result = await self._retrieve(
            vs_retriever,
            retriever,
            llm_model,
            query,
            chain_type
        )

        self.memory.chat_memory.add_ai_message(result['answer'])

        return result
