from litestar import Controller as BaseController
from litestar import handlers
from litestar.datastructures import CacheControlHeader
from litestar.di import Provide
from litestar.response import Response
from litestar.status_codes import HTTP_204_NO_CONTENT

from beaver.api.routes.ping import models as m
from beaver.api.routes.ping.service import Service
from beaver.services.ping.service import PingService


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self) -> Service:
        return Service(
            ping=PingService(),
        )

    def build(self) -> dict[str, Provide]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the ping endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.get(
        summary="Ping",
        cache_control=CacheControlHeader(
            no_store=True,
        ),
        status_code=HTTP_204_NO_CONTENT,
    )
    async def ping(self, service: Service) -> Response[None]:
        """Ping."""

        req = m.PingRequest()

        await service.ping(req)

        return Response(None)

    @handlers.head(
        summary="Ping headers",
        cache_control=CacheControlHeader(
            no_store=True,
        ),
        status_code=HTTP_204_NO_CONTENT,
    )
    async def headping(self, service: Service) -> Response[None]:
        """Ping headers."""

        req = m.HeadPingRequest()

        await service.headping(req)

        return Response(None)
