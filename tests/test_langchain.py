import os
import random
from pathlib import Path

import pytest
from starlette import status

from agent.exceptions import AgentExceptionErrorCode
from agent.enums import HuggingFaceModel


@pytest.mark.asyncio
async def test_langchain_mydata_load(api_version, client, get_service):
    langchain_mydata_service = get_service("LangchainMydataService")
    langchain_mydata_service.set_data_path("test")
    response = await client.get(
        f"/{api_version}/langchain/mydata"
    )
    langchain_mydata_service.set_data_path("mydata")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_langchain_mydata_load_with_empty_dir(mydata_data_dir, api_version, client):
    original_path = Path(mydata_data_dir)
    temp_path = original_path.with_name("temp")
    original_path.rename(temp_path)
    os.mkdir(mydata_data_dir)
    response = await client.get(
        f"/{api_version}/langchain/mydata"
    )
    os.rmdir(mydata_data_dir)
    temp_path.rename(original_path)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail']['error_code'] == AgentExceptionErrorCode.DataFileNotFoundError



@pytest.mark.parametrize(
    "payload",
    [
        ({
            "chunk_size": 1000,
            "chunk_overlap": 200
        }),
    ]
)
@pytest.mark.asyncio
async def test_langchain_mydata_chunk(payload, api_version, client, get_service):
    langchain_mydata_service = get_service("LangchainMydataService")
    langchain_mydata_service.set_data_path("test")
    response = await client.post(
        f"/{api_version}/langchain/mydata/chunk",
        json=payload
    )
    langchain_mydata_service.set_data_path("mydata")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "payload",
    [
        ({
            "chunk_size": 5555,
            "chunk_overlap": -22
        }),
    ]
)
@pytest.mark.asyncio
async def test_langchain_mydata_chunk_invalid_parameter(payload, api_version, client, get_service):
    langchain_mydata_service = get_service("LangchainMydataService")
    langchain_mydata_service.set_data_path("test")
    response = await client.post(
        f"/{api_version}/langchain/mydata/chunk",
        json=payload
    )
    langchain_mydata_service.set_data_path("mydata")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail']['error_code'] == AgentExceptionErrorCode.SplitterParameterError


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
async def test_langchain_mydata_search(payload, api_version, client, get_service):
    response = await client.post(
        f"/{api_version}/langchain/mydata/search",
        json=payload
    )
    assert response.status_code == status.HTTP_200_OK
    res = response.json()
    langchain_mydata_service = get_service("LangchainMydataService")
    assert len(res['documents']) == payload['k']
    assert res['model_name'] == langchain_mydata_service.model_name


@pytest.mark.parametrize(
    "payload",
    [
        ({
            "model_name": random.choice([model.value for model in HuggingFaceModel])
        }),
    ]
)
@pytest.mark.asyncio
async def test_langchain_set_vectorstore(payload, api_version, client, get_service):
    response = await client.post(
        f"/{api_version}/langchain/mydata/vs",
        json=payload
    )
    assert response.status_code == status.HTTP_201_CREATED
    langchain_mydata_service = get_service("LangchainMydataService")
    assert langchain_mydata_service.model_name == payload["model_name"]


@pytest.mark.parametrize(
    "payload",
    [
        ({
            "model_name": "말도_안되는_모델_이름"
        }),
    ]
)
@pytest.mark.asyncio
async def test_langchain_mydata_set_vectorstore_invalid_parameter(payload, api_version, client):
    response = await client.post(
        f"/{api_version}/langchain/mydata/vs",
        json=payload
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail']['error_code'] == AgentExceptionErrorCode.ModelNotFoundError
