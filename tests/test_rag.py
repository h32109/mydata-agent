import uuid

import pytest
from starlette import status

from agent.enums import ChainType, SearchType


@pytest.mark.parametrize(
    "payload",
    [
        ({
            "query": "토큰이 중복 발급되었을 경우 어떻게 되나요?",
            "chain_type": ChainType.MAP_REDUCE.value,
            "search_type": SearchType.MMR.value
        }),
    ]
)
@pytest.mark.asyncio
async def test_rag_retrieve(payload, api_version, client, langchain_ctx):
    response = await client.post(
        f"/{api_version}/rag/retrieve",
        json=payload
    )
    assert response.status_code == status.HTTP_200_OK
    res = response.json()
    assert res['details']['answer']
    assert len(res['details']['source_documents'])
    embedding_model_name = langchain_ctx.get_prod().get_embedding_model_name()
    assert res['details']['embedding_model'] == embedding_model_name


@pytest.mark.parametrize(
    "payload",
    [
        ({
            "query": "토큰이 중복 발급되었을 경우 어떻게 되나요?",
            "chain_type": "말도_안되는_타입",
            "search_type": "말도_안되는_타입"
        }),
    ]
)
@pytest.mark.asyncio
async def test_rag_retrieve_with_invalid_parameter(payload, api_version, client):
    response = await client.post(
        f"/{api_version}/rag/retrieve",
        json=payload
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "payload",
    [
        ({
            "query": "토큰이 중복 발급되었을 경우 어떻게 되나요?"
        }),
    ]
)
@pytest.mark.asyncio
async def test_rag_retrieve_multi_turn(payload, api_version, client, get_service):
    conversation_id = str(uuid.uuid4())
    rag_service = get_service("RAGService")
    response = await client.post(
        f"/{api_version}/rag/retrieve",
        json=payload,
        headers={
            "Conversation-ID": conversation_id
        }
    )
    assert rag_service.get_cache(conversation_id)
    assert len(rag_service.get_cache(conversation_id).chat_memory.messages) == 2
    assert response.status_code == status.HTTP_200_OK
    response = await client.post(
        f"/{api_version}/rag/retrieve",
        json=payload,
        headers={
            "Conversation-ID": conversation_id
        }
    )

    assert rag_service.get_cache(conversation_id)
    assert len(rag_service.get_cache(conversation_id).chat_memory.messages) == 4
    assert response.status_code == status.HTTP_200_OK
