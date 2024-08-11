from fastapi import APIRouter, status

from agent.chatgpt.service import chatgpt_mydata_service
from agent.chatgpt.schema import ChatGPTResponse, ChatGPTReadRequest
from agent.exceptions import BaseAgentException

router = APIRouter()


@router.post(
    "/mydata/retrieve",
    status_code=status.HTTP_200_OK
)
async def retrieve(payload: ChatGPTReadRequest):
    try:
        result = await chatgpt_mydata_service.retrieve(**payload.model_dump())
    except BaseAgentException as e:
        raise e.raise_http(status_code=status.HTTP_400_BAD_REQUEST)
    return ChatGPTResponse(
        msg="Answer from chatGPT",
        details=result
    )
