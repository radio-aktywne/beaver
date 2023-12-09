import pytest
from litestar.testing import AsyncTestClient

from emishows.api.app import AppBuilder
from emishows.config.builder import ConfigBuilder
from emishows.config.models import Config


@pytest.fixture(scope="session")
def config() -> Config:
    """Reusable configuration."""

    return ConfigBuilder().build()


@pytest.fixture(scope="session")
def client(config: Config) -> AsyncTestClient:
    """Reusable test client."""

    app = AppBuilder(config).build()
    return AsyncTestClient(app=app)
