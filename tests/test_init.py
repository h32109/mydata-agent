import pytest


@pytest.mark.asyncio
async def test_chroma_ctx_initialize(chroma_ctx, client):
    assert chroma_ctx.chroma
    assert chroma_ctx.vector_store


@pytest.mark.asyncio
async def test_langchain_ctx_initialize(langchain_ctx, client):
    assert langchain_ctx.db
    assert langchain_ctx.embedding_model_selector
    assert langchain_ctx.llm_model_selector
    assert langchain_ctx.loader_selector
    assert langchain_ctx.splitter_selector
    assert langchain_ctx.retriever_selector