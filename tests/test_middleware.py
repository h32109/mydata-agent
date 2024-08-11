import pytest
from unittest.mock import patch
from starlette import status
from agent.enums import ChainType, RetrieverType, SearchType


@pytest.mark.parametrize(
    "payload",
    [
        ({
            "query": "토큰이 중복 발급되었을 경우 어떻게 되나요?",
            "chain_type": ChainType.MAP_REDUCE.value,
            "retriever_type": RetrieverType.MULTI_QUERY.value,
            "search_type": SearchType.MMR.value
        }),
    ]
)
@pytest.mark.asyncio
async def test_cpu_load_middleware_high_usage(api_version, client, payload):
    with patch('psutil.cpu_percent', return_value=85.0):
        response = await client.post(
            f"/{api_version}/chatgpt/mydata/retrieve",
            json=payload
        )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.parametrize(
    "payload",
    [
        ({
            "query": "토큰이 중복 발급되었을 경우 어떻게 되나요?",
            "chain_type": ChainType.MAP_REDUCE.value,
            "retriever_type": RetrieverType.MULTI_QUERY.value,
            "search_type": SearchType.MMR.value
        }),
    ]
)
@pytest.mark.asyncio
async def test_cpu_load_middleware_normal_usage(api_version, client, payload):
    with patch('psutil.cpu_percent', return_value=50.0):
        response = await client.post(
            f"/{api_version}/chatgpt/mydata/retrieve",
            json=payload
        )
        assert response.status_code == status.HTTP_200_OK

