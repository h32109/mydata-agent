from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from agent.core.config import settings
from agent.routes import (
    api_router,
    view_router
)
from agent.middlewares import (
    CPULoadControlMiddleware,
    CPUMonitorMiddleware
)
from agent.service import ServiceManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_service_manager(settings)
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


async def setup_service_manager(settings):
    await ServiceManager.init(settings)
