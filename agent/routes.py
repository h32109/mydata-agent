from fastapi import APIRouter
from typing import Tuple

from agent.rag.endpoints import router as rag_router
from agent.view.endpoints import router as view_router
from agent.preprocess.endpoints import router as preprocess_router


def create_routers() -> Tuple[APIRouter, APIRouter]:
    api = APIRouter()
    view = APIRouter()

    router_configs = [
        (api, rag_router, '/rag', ["RAG"]),
        (api, preprocess_router, '/preprocess', ["PreProcess"]),
        (view, view_router, '/agent', ["View"])
    ]

    for p, c, prefix, tags in router_configs:
        p.include_router(c, prefix=prefix, tags=tags)

    return api, view
