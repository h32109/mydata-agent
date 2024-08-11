import os

import pytest
from async_asgi_testclient import TestClient


@pytest.fixture
def get_service():
    from agent.service import ServiceManager

    def _get_service(service_name):
        return ServiceManager.get(service_name)

    return _get_service


@pytest.fixture(scope="session")
async def app():
    from agent import create_app
    os.environ["PROFILE"] = "test"
    app_instance = create_app()
    yield app_instance


@pytest.fixture(scope="session")
async def client(app):
    async with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def config():
    from agent.core.config import settings
    os.environ["PROFILE"] = "test"
    return settings


@pytest.fixture(scope="session")
def mydata_data_dir():
    from agent.utils import get_path_from_root
    return get_path_from_root("data/mydata")


@pytest.fixture(scope="session")
def api_version(config):
    return config.API_PREFIX.lstrip("/")
