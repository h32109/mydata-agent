from fastapi import APIRouter, HTTPException
from starlette import status

from agent.preprocess.service import preprocess_service
from agent.preprocess.schema import (
    ChunkRequest,
    VectorStoreRequest,
    SearchRequest,
    LoadRequest
)
from agent.exceptions import BaseAgentException

router = APIRouter()


@router.post(
    "/load",
    status_code=status.HTTP_200_OK
)
async def load(payload: LoadRequest):
    try:
        return await preprocess_service.load(**payload.model_dump(exclude_none=True))
    except BaseAgentException as e:
        raise e.raise_http(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/search",
    status_code=status.HTTP_200_OK
)
async def search(payload: SearchRequest):
    try:
        return await preprocess_service.similarity_search(**payload.model_dump())
    except BaseAgentException as e:
        raise e.raise_http(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/chunk",
    status_code=status.HTTP_200_OK
)
async def chunk(payload: ChunkRequest):
    try:
        return await preprocess_service.chunking(**payload.model_dump(exclude_none=True))
    except BaseAgentException as e:
        raise e.raise_http(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/vs",
    status_code=status.HTTP_201_CREATED
)
async def set_vector_store(payload: VectorStoreRequest):
    try:
        await preprocess_service.save_vector_store(**payload.model_dump(exclude_none=True))
        return {"message": "Vector store saved successfully"}
    except BaseAgentException as e:
        raise e.raise_http(status_code=status.HTTP_400_BAD_REQUEST)
    # except Exception as e:
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
