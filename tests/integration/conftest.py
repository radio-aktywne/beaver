import pytest
import pytest_asyncio
from litestar import Litestar
from litestar.testing import AsyncTestClient

from emishows.api.app import AppBuilder
from emishows.config.builder import ConfigBuilder
from emishows.config.models import Config
from tests.utils.containers import AsyncDockerContainer, ContainerWaiter


@pytest.fixture(scope="session")
def config() -> Config:
    """Loaded configuration."""

    return ConfigBuilder().build()


@pytest.fixture(scope="session")
def app(config: Config) -> Litestar:
    """Reusable application."""

    return AppBuilder(config).build()


@pytest_asyncio.fixture(scope="session")
async def database(config: Config) -> AsyncDockerContainer:
    """Database container."""

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/apps/emishows-db:latest",
        network="host",
        privileged=True,
    )

    async with container as container:
        # Wait for database to start.
        waiter = ContainerWaiter(
            container,
            [
                "./scripts/shell.sh",
                "cockroachdb",
                "sql",
                "--certs-dir",
                "data/certs/",
                "--port",
                str(config.database.port),
                "--execute",
                "''",
            ],
        )
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def emitimes(config: Config) -> AsyncDockerContainer:
    """Emitimes container."""

    container = AsyncDockerContainer(
        "ghcr.io/radio-aktywne/apps/emitimes:latest",
        network="host",
    )

    async with container as container:
        # Wait for emitimes to start.
        waiter = ContainerWaiter(
            container,
            [
                "./scripts/shell.sh",
                "curl",
                "--silent",
                "--head",
                "--fail",
                f"http://localhost:{config.emitimes.port}",
            ],
        )
        await waiter.wait()
        yield container


@pytest_asyncio.fixture(scope="session")
async def client(
    app: Litestar, database: AsyncDockerContainer, emitimes: AsyncDockerContainer
) -> AsyncTestClient:
    """Reusable test client."""

    async with AsyncTestClient(app=app) as client:
        yield client
