import abc

import typing as t

import cachetools
from langchain.retrievers import MultiQueryRetriever, EnsembleRetriever

from langchain_community.document_loaders import PyPDFLoader
from langchain_unstructured import UnstructuredLoader

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter, KonlpyTextSplitter


class SelectorBase:
    key: str | None = None

    def __init__(self, **kwargs):
        self.selects = cachetools.LRUCache(maxsize=1024)

    @abc.abstractmethod
    def update_cache(self, **kwargs):
        pass

    def select(self, key: str | None = None) -> t.Any:
        self.key = key or self.key
        return self.selects[self.key]

    def get(self, key: str | None = None) -> t.Any:
        return self.select(key)


class EmbeddingModelSelector(SelectorBase):
    bge_m3 = HuggingFaceEmbeddings
    ko_sbert_multitask = HuggingFaceEmbeddings
    kf_deberta_multitask = HuggingFaceEmbeddings
    openai = OpenAIEmbeddings

    def __init__(self, huggingface, openai, **kwargs):
        super(EmbeddingModelSelector, self).__init__(**kwargs)
        self.selects["bge_m3"] = self.bge_m3(
            model_name="BAAI/bge-m3",
            **huggingface
        )
        self.selects["ko_sbert_multitask"] = self.ko_sbert_multitask(
            model_name="jhgan/ko-sbert-multitask",
            **huggingface
        )
        self.selects["kf_deberta_multitask"] = self.kf_deberta_multitask(
            model_name="upskyy/kf-deberta-multitask",
            **huggingface
        )
        self.selects["openai"] = self.openai(
            **openai
        )

    def update_cache(self, key, source):
        pass


class LLMModelSelector(SelectorBase):
    openai = ChatOpenAI

    def __init__(self, **kwargs):
        super(LLMModelSelector, self).__init__(**kwargs)
        self.selects["openai"] = self.openai(
            **kwargs['openai']
        )

    def update_cache(self, key, source):
        pass


class LoaderSelector(SelectorBase):
    py_loader = PyPDFLoader
    unstructured_loader = UnstructuredLoader

    def __init__(self, **kwargs):
        super(LoaderSelector, self).__init__(**kwargs)
        self.selects["py_loader"] = self.py_loader
        self.selects["unstructured_loader"] = self.unstructured_loader

    def update_cache(self, key, source):
        pass


class SplitterSelector(SelectorBase):
    recursive_character_spliter = RecursiveCharacterTextSplitter
    character_spliter = CharacterTextSplitter
    konlpy_spliter = KonlpyTextSplitter

    def __init__(self, **kwargs):
        super(SplitterSelector, self).__init__(**kwargs)
        self.selects["recursive_character_spliter"] = self.recursive_character_spliter(**kwargs)
        self.selects["character_spliter"] = self.character_spliter(**kwargs)
        self.selects["konlpy_spliter"] = self.konlpy_spliter(**kwargs)

    def update_cache(self, key, source):
        pass


class RetrieverSelector(SelectorBase):
    default = None
    multiquery_retriever = MultiQueryRetriever
    ensemble_retriever = EnsembleRetriever

    def __init__(self, **kwargs):
        super(RetrieverSelector, self).__init__(**kwargs)
        self.selects["default"] = self.default
        self.selects["multiquery_retriever"] = self.multiquery_retriever
        self.selects["ensemble_retriever"] = self.ensemble_retriever

    def update_cache(self, key, source):
        pass
