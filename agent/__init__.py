from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from agent.context.langchain_ctx.ctx import LangchainCtx
from agent.context.chroma_ctx.ctx import ChromaCtx
from agent.core.config import settings
from agent.routes import create_routers
from agent.middlewares import (
    CPULoadControlMiddleware,
    CPUMonitorMiddleware
)
from agent.service import Service

import asyncio

asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())


@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_context(settings)
    setup_service_manager(settings)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.is_dev else None,
        lifespan=lifespan
    )

    setup_routers(app)
    setup_middlewares(app)

    return app


def setup_routers(app: FastAPI):
    api_router, view_router = create_routers()
    app.include_router(api_router, prefix=settings.API_PREFIX)
    app.include_router(view_router)


def setup_middlewares(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        CPULoadControlMiddleware,
        high_cpu_threshold=0.8
    )
    # app.add_middleware(
    #     CPUMonitorMiddleware,
    #     duration=5,
    #     interval=0.1
    # )


def setup_service_manager(settings):
    Service.init(settings)


async def setup_context(settings):
    ChromaCtx.init(settings)
    LangchainCtx.init(settings)
    from agent.globals import cm, lc
    await cm.start()
    await lc.start(settings)
