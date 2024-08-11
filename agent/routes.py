from fastapi import APIRouter

from agent.chatgpt.endpoints import router as chatgpt_router
from agent.view.endpoints import router as _view_router
from agent.langchain_.endpoints import router as langchain_router

api_router = APIRouter()

api_router.include_router(chatgpt_router, prefix='/chatgpt', tags=["ChatGPT"])
api_router.include_router(langchain_router, prefix='/langchain', tags=["ChatGPT"])

view_router = APIRouter()

view_router.include_router(_view_router, prefix='/view', tags=["View"])
