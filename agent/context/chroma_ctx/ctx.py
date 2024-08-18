import typing as t
from uuid import uuid4

import chromadb
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_chroma import Chroma
from langchain_core.documents import Document

from ..base import Context
from ...utils import get_path_from_root

Collections = ["documents", "chunked_documents"]
CollectionLiteral = t.Literal[*Collections]


class ChromaCtx(Context):

    def __init__(self, settings, chroma: chromadb.Client):
        self.settings = settings
        self.chroma = chroma
        self.vector_store: Chroma | None = None

    @classmethod
    def init(cls, settings, **kwargs):
        chroma = chromadb.Client()
        ctx = ChromaCtx(settings, chroma)
        ctx.register("chroma", ctx)
        return ctx

    async def start(self):
        for collection in Collections:
            self.create_collection(collection)

    def create_collection(self, collection: CollectionLiteral):
        self.chroma.create_collection(name=collection, metadata={"hnsw:space": "cosine"})

    def get_collection(self, collection: CollectionLiteral) -> chromadb.api.Collection:
        return self.chroma.get_collection(collection)

    def delete_collection(self, collection: CollectionLiteral):
        self.chroma.delete_collection(collection)

    def get_vector_store(self) -> Chroma | None:
        return self.vector_store

    async def save_docs(self, collection, docs, refresh=False):
        if refresh:
            self.delete_collection(collection)
            self.create_collection(collection)

        collection = self.get_collection(collection)

        documents = [doc.page_content for doc in docs]
        metadatas = [
            {k: v for k, v in doc.metadata.items() if not isinstance(v, list)}
            for doc in docs
        ]
        ids = [str(uuid4()) for _ in range(len(docs))]

        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    async def get_docs(self, collection):
        collection = self.get_collection(collection)
        existing_count = collection.count()
        batch_size = 100
        docs = []

        for i in range(0, existing_count, batch_size):

            batch = collection.get(
                limit=batch_size,
                offset=i)

            docs.extend([
                Document(page_content=d, metadata=m)
                for d, m in zip(batch["documents"], batch["metadatas"])
            ])
        return docs

    async def save_vector_store(self, collection, embedder, model_name):
        store = LocalFileStore(get_path_from_root('cache'))

        cached_embedder = CacheBackedEmbeddings.from_bytes_store(
            embedder, store, namespace=model_name
        )

        if self.vector_store:
            self.vector_store.reset_collection()

        chunks = await self.get_docs(collection)

        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=cached_embedder
        )
