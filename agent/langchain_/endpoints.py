from fastapi import APIRouter
from starlette import status

from agent.langchain_.service import langchain_mydata_service
from agent.langchain_.schema import (
    LangChainChunkRequest,
    LangChainVectorStoreRequest,
    LangChainSearchRequest
)
from agent.exceptions import BaseAgentException

router = APIRouter()


@router.get(
    "/mydata",
    status_code=status.HTTP_200_OK
)
async def load():
    try:
        return await langchain_mydata_service.load()
    except BaseAgentException as e:
        raise e.raise_http(status_code=status.HTTP_400_BAD_REQUEST)


@router.post(
    "/mydata/search",
    status_code=status.HTTP_200_OK
)
async def search(payload: LangChainSearchRequest):
    try:
        return await langchain_mydata_service.similarity_search(**payload.model_dump())
    except BaseAgentException as e:
        raise e.raise_http(status_code=status.HTTP_400_BAD_REQUEST)


@router.post(
    "/mydata/chunk",
    status_code=status.HTTP_200_OK
)
async def chunk(payload: LangChainChunkRequest):
    try:
        return await langchain_mydata_service.chunking(**payload.model_dump())
    except BaseAgentException as e:
        raise e.raise_http(status_code=status.HTTP_400_BAD_REQUEST)


@router.post(
    "/mydata/vs",
    status_code=status.HTTP_201_CREATED
)
async def set_vector_store(payload: LangChainVectorStoreRequest):
    try:
        await langchain_mydata_service.set_vector_store(**payload.model_dump())
    except BaseAgentException as e:
        raise e.raise_http(status_code=status.HTTP_400_BAD_REQUEST)
    return status.HTTP_201_CREATED
