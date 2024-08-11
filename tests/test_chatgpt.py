import pytest
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
async def test_chatgpt_mydata_retrieve(payload, api_version, client, get_service):
    response = await client.post(
        f"/{api_version}/chatgpt/mydata/retrieve",
        json=payload
    )
    assert response.status_code == status.HTTP_200_OK
    res = response.json()
    langchain_mydata_service = get_service("LangchainMydataService")
    assert res['details']['result']
    assert len(res['details']['source_documents'])
    assert res['details']['embedding_model'] == langchain_mydata_service.model_name


@pytest.mark.parametrize(
    "payload",
    [
        ({
            "query": "토큰이 중복 발급되었을 경우 어떻게 되나요?",
            "chain_type": "말도_안되는_타입",
            "retriever_type": "말도_안되는_타입",
            "search_type": "말도_안되는_타입"
        }),
    ]
)
@pytest.mark.asyncio
async def test_chatgpt_mydata_retrieve_with_invalid_parameter(payload, api_version, client):
    response = await client.post(
        f"/{api_version}/chatgpt/mydata/retrieve",
        json=payload
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
