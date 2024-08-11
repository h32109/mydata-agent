import pytest

@pytest.mark.asyncio
async def test_app_initialize(get_service, client):
    langchain_mydata_service = get_service("LangchainMydataService")
    assert langchain_mydata_service.data_path
    assert langchain_mydata_service.model_name
    assert langchain_mydata_service.faiss_path
    assert langchain_mydata_service.vector_store

