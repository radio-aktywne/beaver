import logging
from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from importlib import metadata

from litestar import Litestar, Router
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.contrib.pydantic import PydanticPlugin
from litestar.openapi import OpenAPIConfig
from litestar.plugins import PluginProtocol

from emishows.api.routes.router import router
from emishows.config.models import Config
from emishows.services.datashows.service import DatashowsService
from emishows.services.datatimes.service import DatatimesService
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

    def _get_debug(self) -> bool:
        return self._config.debug

    @asynccontextmanager
    async def _suppress_httpx_logging_lifespan(
        self, app: Litestar
    ) -> AsyncGenerator[None]:
        logger = logging.getLogger("httpx")
        disabled = logger.disabled
        logger.disabled = True

        try:
            yield
        finally:
            logger.disabled = disabled

    @asynccontextmanager
    async def _datashows_lifespan(self, app: Litestar) -> AsyncGenerator[None]:
        state: State = app.state

        async with state.datashows:
            yield

    def _build_lifespan(
        self,
    ) -> list[Callable[[Litestar], AbstractAsyncContextManager]]:
        return [
            self._suppress_httpx_logging_lifespan,
            self._datashows_lifespan,
        ]

    def _build_openapi_config(self) -> OpenAPIConfig:
        return OpenAPIConfig(
            # Title of the service
            title="emishows",
            # Version of the service
            version=metadata.version("emishows"),
            # Description of the service
            summary="Broadcast shows 🎭",
            # Use handler docstrings as operation descriptions
            use_handler_docstrings=True,
            # Endpoint to serve the OpenAPI docs from
            path="/schema",
        )

    def _build_channels_plugin(self) -> ChannelsPlugin:
        return ChannelsPlugin(
            # Store events in memory (good only for single instance services)
            backend=MemoryChannelsBackend(),
            # Channels to handle
            channels=["events"],
            # Don't allow channels outside of the list above
            arbitrary_channels_allowed=False,
        )

    def _build_pydantic_plugin(self) -> PydanticPlugin:
        return PydanticPlugin(
            # Use aliases for serialization
            prefer_alias=True,
            # Allow type coercion
            validate_strict=False,
        )

    def _build_plugins(self) -> list[PluginProtocol]:
        return [
            self._build_channels_plugin(),
            self._build_pydantic_plugin(),
        ]

    def _build_datashows(self) -> DatashowsService:
        return DatashowsService(
            datasource={
                "url": self._config.datashows.sql.url,
            },
        )

    def _build_datatimes(self) -> DatatimesService:
        return DatatimesService(
            config=self._config.datatimes,
        )

    def _build_initial_state(self) -> State:
        config = self._config
        datashows = self._build_datashows()
        datatimes = self._build_datatimes()

        return State(
            {
                "config": config,
                "datashows": datashows,
                "datatimes": datatimes,
            }
        )

    def build(self) -> Litestar:
        return Litestar(
            route_handlers=self._get_route_handlers(),
            debug=self._get_debug(),
            lifespan=self._build_lifespan(),
            openapi_config=self._build_openapi_config(),
            plugins=self._build_plugins(),
            state=self._build_initial_state(),
        )
