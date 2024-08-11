import typing as t

from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.retrievers import MultiQueryRetriever
from langchain_openai import ChatOpenAI

from agent.service import ServiceManager, ServiceBase
from agent.chatgpt.schema import ChatGPTDocument
from agent.enums import RetrieverType


class ChatGPTServiceBase(ServiceBase):
    langchain_service: str
    settings: t.Any
    model: t.Any

    def __init__(self, langchain_service: str):
        self.langchain_service = langchain_service

    def configuration(self, settings):
        self.settings = settings
        self.model = ChatOpenAI(
            model=self.settings.OPENAI_MODEL,
            openai_api_key=self.settings.OPENAI_API_KEY,
            temperature=self.settings.TEMPERATURE,
        )


class ChatGPTMydataService(ChatGPTServiceBase):

    def _wrap_result(self, result):
        langchain_service = ServiceManager.get(self.langchain_service)
        source_documents = result.pop("source_documents")
        return {
            **result,
            "source_documents": [
                ChatGPTDocument(**dict(s)).model_dump() for s in source_documents
            ],
            "model": self.model.model_name,
            "embedding_model": langchain_service.get_model_name()
        }

    async def retrieve(self, query, chain_type, retriever_type, search_type):
        langchain_service = ServiceManager.get(self.langchain_service)
        vector_store = langchain_service.get_vector_store()

        retriever = vector_store.as_retriever(
            search_type=search_type,
            search_kwargs={"k": 3, "fetch_k": 10}
        )

        if retriever_type == RetrieverType.MULTI_QUERY:
            retriever = MultiQueryRetriever.from_llm(
                retriever=retriever,
                llm=self.model
            )

        qa = RetrievalQA.from_chain_type(
            llm=self.model,
            chain_type=chain_type,
            retriever=retriever,
            return_source_documents=True
        )

        return self._wrap_result(qa.invoke(query))


chatgpt_mydata_service = ServiceManager.add_service(ChatGPTMydataService("LangchainMydataService"))
