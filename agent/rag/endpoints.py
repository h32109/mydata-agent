from fastapi import APIRouter, status, HTTPException, Header

from agent.rag.service import rag_service
from agent.rag.schema import RAGResponse, RAGRequest
from agent.exceptions import BaseAgentException

router = APIRouter()


@router.post(
    "/retrieve",
    response_model=RAGResponse,
    status_code=status.HTTP_200_OK
)
async def retrieve(
        payload: RAGRequest,
        conversation_id: str | None = Header("chat_history", alias="Conversation-ID")
) -> RAGResponse:
    try:
        result = await rag_service.retrieve(**payload.model_dump(exclude_none=True), conversation_id=conversation_id)
        return RAGResponse(msg="Answer from agent", details=result)
    except BaseAgentException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
