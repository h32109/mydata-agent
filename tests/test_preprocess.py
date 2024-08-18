import os
from pathlib import Path

import pytest
from starlette import status

from agent.exceptions import AgentExceptionErrorCode


@pytest.mark.parametrize(
    "payload",
    [
        ({
            "loader": "py_loader",
            "sync": True
        }),
    ]
)
@pytest.mark.asyncio
async def test_preprocess_load_and_save(payload, api_version, client, langchain_ctx):
    response = await client.post(
        f"/{api_version}/preprocess/load",
        json=payload
    )
    assert response.status_code == status.HTTP_200_OK
    res = response.json()
    docs = await langchain_ctx.get_prod().get_docs()
    assert res
    assert len(res) == len(docs)


@pytest.mark.parametrize(
    "payload",
    [
        ({
            "loader": "py_loader",
            "sync": True
        }),
    ]
)
@pytest.mark.asyncio
async def test_preprocess_load_with_empty_dir(mydata_data_dir, payload, api_version, client):
    original_path = Path(mydata_data_dir)
    temp_path = original_path.with_name("temp")
    original_path.rename(temp_path)
    os.mkdir(mydata_data_dir)
    response = await client.post(
        f"/{api_version}/preprocess/load",
        json=payload
    )
    os.rmdir(mydata_data_dir)
    temp_path.rename(original_path)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail']['error_code'] == AgentExceptionErrorCode.DataFileNotFoundError


@pytest.mark.parametrize(
    "payload",
    [
        ({
            "splitter": "konlpy_spliter",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "sync": True
        }),
    ]
)
@pytest.mark.asyncio
async def test_preprocess_chunk_and_save(payload, api_version, client, get_service, langchain_ctx):
    response = await client.post(
        f"/{api_version}/preprocess/chunk",
        json=payload
    )
    assert response.status_code == status.HTTP_200_OK
    res = response.json()
    chunks = await langchain_ctx.get_prod().get_chunked_docs()
    assert res
    assert len(res) == len(chunks)


@pytest.mark.parametrize(
    "payload",
    [
        ({
            "query": "토큰이 중복 발급되었을 경우 어떻게 되나요?",
            "k": 3
        }),
    ]
)
@pytest.mark.asyncio
async def test_preprocess_search(payload, api_version, client, get_service):
    response = await client.post(
        f"/{api_version}/preprocess/search",
        json=payload
    )
    assert response.status_code == status.HTTP_200_OK
    res = response.json()
    assert len(res) == payload['k']


@pytest.mark.parametrize(
    "payload",
    [
        ({
            "embedding_model": "ko_sbert_multitask"
        }),
    ]
)
@pytest.mark.asyncio
async def test_langchain_set_vectorstore(payload, api_version, client, langchain_ctx):
    response = await client.post(
        f"/{api_version}/preprocess/vs",
        json=payload
    )
    assert response.status_code == status.HTTP_201_CREATED
    embedding_model_name = langchain_ctx.get_prod().get_embedding_model_name()
    assert str(embedding_model_name).endswith(str(payload["embedding_model"]).replace("_", "-"))
