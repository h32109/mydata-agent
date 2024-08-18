import typing as t

import tiktoken
from pydantic import BaseModel

from ..base import Context
from .plugins import Loader, Splitter

from .store_prod import StoreProd

from .selector import (
    EmbeddingModelSelector,
    LLMModelSelector,
    LoaderSelector,
    SplitterSelector,
    RetrieverSelector

)
from agent.utils import get_path_from_root

from . import logger


EmbeddingModelLiteral = t.Literal["ko_sbert_multitask", "kf_deberta_multitask", "bge_m3", "openai"]
LLMModelLiteral = t.Literal["openai"]
LoaderLiteral = t.Literal["py_loader", "unstructured_loader"]
SplitterLiteral = t.Literal["recursive_character_spliter", "character_spliter", "konlpy_spliter"]
RetrieverLiteral = t.Literal["default", "multiquery_retriever", "ensemble_retriever"]


class LangchainParameterBase(BaseModel):
    embedding_model: EmbeddingModelLiteral | None = None
    llm_model: LLMModelLiteral | None = None
    loader: LoaderLiteral | None = None
    splitter: SplitterLiteral | None = None
    retriever: RetrieverLiteral | None = None
    sync: bool | None = None


class LangchainCtx(Context):
    domain: str

    def __init__(self,
                 settings,
                 db,
                 embedding_model_selector,
                 llm_model_selector,
                 loader_selector,
                 splitter_selector,
                 retriever_selector
                 ):
        super().__init__()
        self.settings = settings
        self.db = db
        self.embedding_model_selector = embedding_model_selector
        self.llm_model_selector = llm_model_selector
        self.loader_selector = loader_selector
        self.splitter_selector = splitter_selector
        self.retriever_selector = retriever_selector

    def create_prod(self,
                    embedding_model,
                    llm_model,
                    loader,
                    splitter,
                    retriever) -> StoreProd:
        prod = StoreProd(
            self.settings,
            self.db,
            embedding_model,
            llm_model,
            loader,
            splitter,
            retriever
        )
        return prod

    def get_prod(
            self,
            llm_model: LLMModelLiteral | None = None,
            embedding_model: EmbeddingModelLiteral | None = None,
            loader: LoaderLiteral | None = None,
            splitter: SplitterLiteral | None = None,
            retriever: RetrieverLiteral | None = None
    ) -> StoreProd:
        embedding_model = self.embedding_model_selector.select(embedding_model)
        llm_model = self.llm_model_selector.select(llm_model)
        loader = self.loader_selector.select(loader)
        splitter = self.splitter_selector.select(splitter)
        retriever = self.retriever_selector.select(retriever)
        return self.create_prod(
            embedding_model,
            llm_model,
            loader,
            splitter,
            retriever
        )

    @classmethod
    def init(cls, settings, **kwargs):
        db = cls.get(settings.DEFAULT_DATABASE)
        # TODO: error

        model_kwargs = {'device': settings.EMBEDDING_DEVICE}
        encode_kwargs = {'normalize_embeddings': True}

        embedding_model_selector = EmbeddingModelSelector(
            huggingface={
                'model_kwargs': model_kwargs,
                'encode_kwargs': encode_kwargs
            },
            openai={
                "openai_api_key": settings.OPENAI_API_KEY
            }
        )

        llm_model_selector = LLMModelSelector(
            openai={
                "model": settings.OPENAI_MODEL,
                "openai_api_key": settings.OPENAI_API_KEY,
                "temperature": settings.TEMPERATURE
            }
        )

        loader_selector = LoaderSelector()

        tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")

        splitter_selector = SplitterSelector(
            chunk_size=settings.DEFAULT_CHUNK_SIZE,
            chunk_overlap=settings.DEFAULT_CHUNK_OVERLAP,
            length_function=lambda text: len(tokenizer.encode(text))
        )

        retriever_selector = RetrieverSelector()

        ctx = LangchainCtx(
            settings=settings,
            db=db,
            embedding_model_selector=embedding_model_selector,
            llm_model_selector=llm_model_selector,
            loader_selector=loader_selector,
            splitter_selector=splitter_selector,
            retriever_selector=retriever_selector
        )

        ctx.register("langchain", ctx)

    async def start(self, settings):
        logger.info("Starting LangchainCtx initialization...")
        self.domain = settings.DOMAIN
        logger.info(f"Domain set to: {self.domain}")

        logger.info("Creating production instance...")
        prod = self.get_prod(
            llm_model=settings.DEFAULT_LLM_MODEL,
            embedding_model=settings.DEFAULT_EMBEDDING_MODEL,
            loader=settings.DEFAULT_LOADER,
            splitter=settings.DEFAULT_SPLITTER,
            retriever=settings.DEFAULT_RETRIEVER
        )
        logger.info("Production instance created successfully")

        data_path = get_path_from_root(f'data/{self.domain}')
        logger.info(f"Data path set to: {data_path}")

        Loader.set_data_path(data_path)
        logger.info("Loading documents...")
        docs = await prod(Loader).load()
        logger.info(f"Loaded {len(docs)} documents")

        logger.info("Saving documents...")
        await prod.save_docs(docs)
        logger.info("Documents saved successfully")

        logger.info("Chunking documents...")
        chunks = await prod(Splitter).chunking(docs, self.settings.DEFAULT_CHUNK_SIZE, self.settings.DEFAULT_CHUNK_OVERLAP)
        logger.info(f"Created {len(chunks)} chunks")

        logger.info("Saving chunked documents...")
        await prod.save_chunked_docs(chunks)
        logger.info("Chunked documents saved successfully")

        logger.info("Saving vector store...")
        await prod.save_vector_store()
        logger.info("Vector store saved successfully")

        logger.info("LangchainCtx initialization completed")
