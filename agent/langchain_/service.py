import asyncio
import itertools
import os
import typing as t

import tiktoken

from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from agent.service import ServiceManager, ServiceBase
from agent.enums import FileExtension
from agent.langchain_.schema import LangChainSearchResponse
from agent.utils import (
    get_files_recursive,
    get_path_from_root,
    get_ext
)
from agent.exceptions import (
    ModelNotFoundError,
    DataFileNotFoundError,
    SplitterParameterError
)


class LangChainServiceBase(ServiceBase):
    settings: t.Any
    vector_store: t.Any
    domain: str
    data_path: str
    faiss_path: str
    model_name: str

    def __init__(self, domain: str):
        self.domain = domain

    def _set_faiss_folder_name(self, model_name):
        folder_name = f'faiss_index_{model_name.replace("/", "_")}_{self.settings.CHUNK_SIZE}_{self.settings.EMBEDDING_DEVICE.value}'
        self.faiss_path = f'{self.data_path}/{folder_name}'

    async def _load_pdf(self, file_path):
        loader = PyPDFLoader(file_path)
        return loader.load_and_split()

    async def _load(self):
        file_paths = get_files_recursive(self.data_path)
        if not file_paths:
            raise DataFileNotFoundError(
                "읽어 올 파일이 없습니다. 데이터 파일을 확인해 주세요."
            )
        load_tasks = []
        for file_path in file_paths:
            file_ext = get_ext(file_path)
            match file_ext:
                case FileExtension.PDF.value:
                    load_tasks.append(self._load_pdf(file_path))
                case _:
                    continue
        docs = await asyncio.gather(*load_tasks)
        return list(itertools.chain(*docs))

    async def _chunking(self, docs, chunk_size, chunk_overlap):
        tokenizer = tiktoken.get_encoding("cl100k_base")

        if not 1 <= chunk_overlap <= 5000 or not 1 <= chunk_size <= 5000:
            raise SplitterParameterError(
                "Chunk_overlap과 chunk_size는 반드시 1과 5000사이의 정수여야 합니다."
            )

        text_spliter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=lambda text: len(tokenizer.encode(text))
        )
        chunks = text_spliter.split_documents(docs)
        return chunks

    async def _get_model(self, model_name):
        model_kwargs = {'device': self.settings.EMBEDDING_DEVICE}
        encode_kwargs = {'normalize_embeddings': True}
        try:
            hf = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )
        except Exception as e:
            raise ModelNotFoundError(
                f"{model_name} 해당 모델을 hugging-face에서 찾을 수 없습니다."
            )
        return hf

    async def _store_vectors(self, chunks, model):
        store = LocalFileStore(get_path_from_root('cache'))

        cached_embedder = CacheBackedEmbeddings.from_bytes_store(
            model, store, namespace=model.model_name
        )

        vector_store = FAISS.from_documents(
            documents=chunks,
            embedding=cached_embedder
        )
        vector_store.save_local(self.faiss_path)

        self.vector_store = vector_store

    async def _load_vector_store(self, model):
        vector_store = FAISS.load_local(
            folder_path=self.faiss_path,
            embeddings=model,
            allow_dangerous_deserialization=True
        )
        self.vector_store = vector_store

    async def _set_vector_store(self, model):
        self.model_name = model.model_name
        self._set_faiss_folder_name(self.model_name)
        if self.settings.REFRESH_VECTOR_STORE or not os.path.exists(self.faiss_path):
            docs = await self._load()
            chunks = await self._chunking(docs, self.settings.CHUNK_SIZE, self.settings.CHUNK_OVERLAP)
            await self._store_vectors(chunks=chunks, model=model)
        else:
            await self._load_vector_store(model)

    async def configuration(self, settings):
        self.settings = settings
        self.data_path = get_path_from_root(f'data/{self.domain}')
        model = await self._get_model(self.settings.DEFAULT_EMBEDDING_MODEL)
        await self._set_vector_store(model)


class LangchainService(LangChainServiceBase):

    def _wrap_result(self, result):
        return LangChainSearchResponse(
            documents=[dict(r) for r in result],
            model_name=self.get_model_name()
        )

    def get_model_name(self):
        return self.model_name

    def get_vector_store(self):
        return self.vector_store

    def set_data_path(self, path):
        self.data_path = get_path_from_root(f'data/{path}')

    async def similarity_search(self, query, k):
        result = self.vector_store.similarity_search(query, k)
        return self._wrap_result(result)

    async def load(self):
        return await self._load()

    async def chunking(self, chunk_size, chunk_overlap):
        docs = await self._load()
        chunks = await self._chunking(docs, chunk_size, chunk_overlap)
        return chunks

    async def set_vector_store(self, model_name):
        model = await self._get_model(model_name)
        await self._set_vector_store(model)


class LangchainMydataService(LangchainService):
    ...


langchain_mydata_service = ServiceManager.add_service(LangchainMydataService("mydata"))
