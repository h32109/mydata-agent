import typing as t
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document


class StoreProd:
    def __init__(
            self,
            settings,
            db,
            embedding_model,
            llm_model,
            loader,
            splitter,
            retriever
    ):
        self.settings = settings
        self.db = db
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.loader = loader
        self.splitter = splitter
        self.retriever = retriever

    def __call__(self, plugin, *args, **kwargs):
        return plugin(self, *args, **kwargs)

    def get_component(self, component_name: str):
        return getattr(self, component_name)

    get_loader = lambda self: self.get_component('loader')
    get_splitter = lambda self: self.get_component('splitter')
    get_retriever = lambda self: self.get_component('retriever')
    get_llm_model = lambda self: self.get_component('llm_model')
    get_embedding_model = lambda self: self.get_component('embedding_model')
    get_embedding_model_name = lambda self: self.get_model_name(self.embedding_model)
    get_llm_model_name = lambda self: self.get_model_name(self.llm_model)

    def get_model_name(self, model) -> str:
        return model.model if isinstance(model, OpenAIEmbeddings) else model.model_name

    async def save_docs(self, docs: t.List[Document], sync=False):
        await self.db.save_docs("documents", docs, refresh=sync)

    async def save_chunked_docs(self, chunked_docs: t.List[Document], sync=False):
        await self.db.save_docs("chunked_documents", chunked_docs, refresh=sync)

    async def get_docs(self) -> t.List[Document]:
        return await self.db.get_docs("documents")

    async def get_chunked_docs(self) -> t.List[Document]:
        return await self.db.get_docs("chunked_documents")

    async def save_vector_store(self):
        model_name = self.get_model_name(self.embedding_model)
        await self.db.save_vector_store("chunked_documents", self.embedding_model, model_name=model_name)

    def get_vector_store_retriever(self, search_type: str, k: int = 3):
        vector_store = self.db.get_vector_store()
        return vector_store.as_retriever(search_type=search_type, search_kwargs={"k": k})

    async def similarity_search(self, query: str, k: int) -> t.List[Document]:
        vector_store = self.db.get_vector_store()
        return await vector_store.asimilarity_search(query, k)
