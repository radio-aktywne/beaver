import logging
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from importlib import metadata
from typing import AsyncGenerator, Callable

from litestar import Litestar, Router
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.contrib.pydantic import PydanticPlugin
from litestar.openapi import OpenAPIConfig
from litestar.plugins import PluginProtocol
from prisma import Prisma

from emishows.api.routes.router import router
from emishows.config.models import Config
from emishows.emitimes.service import EmitimesService
from emishows.state import State


class AppBuilder:
    """Builds the app.

    Args:
        config: Config object.
    """

    def __init__(self, config: Config) -> None:
        self._config = config

    def _get_route_handlers(self) -> list[Router]:
        return [router]

    def _build_openapi_config(self) -> OpenAPIConfig:
        return OpenAPIConfig(
            title="emishows app",
            version=metadata.version("emishows"),
            description="Emission shows 🎭",
        )

    def _build_channels_plugin(self) -> ChannelsPlugin:
        return ChannelsPlugin(
            backend=MemoryChannelsBackend(),
            channels=["events"],
        )

    def _build_pydantic_plugin(self) -> PydanticPlugin:
        return PydanticPlugin(
            prefer_alias=True,
        )

    def _build_plugins(self) -> list[PluginProtocol]:
        return [
            self._build_channels_plugin(),
            self._build_pydantic_plugin(),
        ]

    def _build_database_url(self) -> str:
        return f"postgres://user:{self._config.database.password}@{self._config.database.host}:{self._config.database.port}/database"

    def _build_initial_state(self) -> State:
        return State(
            {
                "config": self._config,
                "prisma": Prisma(datasource={"url": self._build_database_url()}),
                "emitimes": EmitimesService(self._config.emitimes),
            }
        )

    @asynccontextmanager
    async def _suppress_httpx_logging_lifespan(
        self, app: Litestar
    ) -> AsyncGenerator[None, None]:
        logger = logging.getLogger("httpx")
        disabled = logger.disabled
        logger.disabled = True

        try:
            yield
        finally:
            logger.disabled = disabled

    @asynccontextmanager
    async def _prisma_lifespan(self, app: Litestar) -> AsyncGenerator[None, None]:
        state: State = app.state

        async with state.prisma:
            yield

    def _build_lifespan(
        self,
    ) -> list[Callable[[Litestar], AbstractAsyncContextManager]]:
        return [
            self._suppress_httpx_logging_lifespan,
            self._prisma_lifespan,
        ]

    def build(self) -> Litestar:
        return Litestar(
            route_handlers=self._get_route_handlers(),
            openapi_config=self._build_openapi_config(),
            plugins=self._build_plugins(),
            state=self._build_initial_state(),
            lifespan=self._build_lifespan(),
        )
