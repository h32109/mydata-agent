import typing as t

from langchain_core.documents import Document

from agent.context.langchain_ctx import Loader, Splitter
from agent.globals import lc
from agent.service import Service, ServiceBase


class PreprocessServiceBase(ServiceBase):
    settings: t.Any

    def configuration(self, settings: t.Any) -> None:
        self.settings = settings


class PreprocessService(PreprocessServiceBase):

    async def similarity_search(self, query: str, k: int) -> t.List[Document]:
        prod = lc.get_prod()
        result = await prod.similarity_search(query, k)
        return result

    async def load(self, loader: str, sync: bool | None = None) -> t.List[Document]:
        prod = lc.get_prod(loader=loader)
        docs = await prod(Loader).load()
        if sync:
            await prod.save_docs(docs=docs, sync=sync)
        return docs

    async def chunking(self, splitter: str, chunk_size: int, chunk_overlap: int, sync: bool | None = None) -> t.List[
        Document]:
        prod = lc.get_prod(splitter=splitter)
        docs = await prod.get_docs()
        chunks = await prod(Splitter).chunking(docs, chunk_size, chunk_overlap)
        if sync:
            await prod.save_chunked_docs(chunked_docs=chunks, sync=sync)
        return chunks

    async def save_vector_store(self, embedding_model: str) -> None:
        await lc.get_prod(embedding_model=embedding_model).save_vector_store()


preprocess_service = Service.add_service(PreprocessService)
