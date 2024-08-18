__all__ = ('Loader',)

import asyncio

from langchain_community.document_loaders import PyPDFLoader
from langchain_unstructured import UnstructuredLoader
from unstructured_client import UnstructuredClient

from agent.enums import FileExtension
from agent.exceptions import DataFileNotFoundError
from agent.utils import get_ext, get_files_recursive
from .base import PluginBase

from urllib3.exceptions import InsecureRequestWarning
import requests

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Loader(PluginBase):
    data_path: str

    def __init__(
            self,
            prod,
            *args,
            **kwargs
    ):
        super(Loader, self).__init__(prod, *args, **kwargs)

    @classmethod
    def set_data_path(cls, data_path):
        cls.data_path = data_path

    def _load_pdf(self, file_path):
        if self.prod.loader == PyPDFLoader:
            loader = self.prod.loader(file_path)
            return loader.load()
        elif self.prod.loader == UnstructuredLoader:
            client = UnstructuredClient(
                api_key_auth=self.prod.settings.UNSTRUCTURED_API_KEY,
                client=requests.Session(),
                server_url="https://api.unstructuredapp.io/general/v0/general",
            )
            loader: UnstructuredLoader = self.prod.loader(
                file_path=file_path,
                client=client,
                partition_via_api=True,
                chunking_strategy="by_title",
                strategy="fast",
            )
            return loader.load()

    async def load(self, data_path: str | None = None):
        file_paths = get_files_recursive(data_path or self.data_path)
        if not file_paths:
            raise DataFileNotFoundError("읽어 올 파일이 없습니다. 데이터 파일을 확인해 주세요.")

        docs = []
        for file_path in file_paths:
            if get_ext(file_path) == FileExtension.PDF.value:
                result = await asyncio.to_thread(self._load_pdf, file_path)
                docs.extend(result)
        return docs
