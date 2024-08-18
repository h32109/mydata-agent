__all__ = ('Splitter', )

from .base import PluginBase


class Splitter(PluginBase):

    def __init__(
            self,
            prod,
            *args,
            **kwargs
    ):
        super(Splitter, self).__init__(prod, *args, **kwargs)

    async def chunking(self, docs, chunk_size, chunk_overlap):
        splitter = self.prod.get_splitter()
        if chunk_size:
            splitter.chunk_size = chunk_size
        if chunk_overlap:
            splitter.chunk_overlap = chunk_overlap
        chunks = splitter.split_documents(docs)
        return chunks
