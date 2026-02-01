from collections.abc import Mapping
from typing import Annotated

from litestar import Controller as BaseController
from litestar import handlers
from litestar.channels import ChannelsPlugin
from litestar.di import Provide
from litestar.params import Parameter
from litestar.response import Response

from beaver.api.exceptions import BadRequestException
from beaver.api.routes.schedule import errors as e
from beaver.api.routes.schedule import models as m
from beaver.api.routes.schedule.service import Service
from beaver.models.base import Jsonable, Serializable
from beaver.services.mevents.service import EventsService
from beaver.state import State


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(
        self,
        state: State,
        channels: ChannelsPlugin,
    ) -> Service:
        return Service(
            events=EventsService(
                howlite=state.howlite, sapphire=state.sapphire, channels=channels
            )
        )

    def build(self) -> Mapping[str, Provide]:
        """Build the dependencies."""
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the schedules endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.get(
        summary="List schedules",
    )
    async def list(  # noqa: PLR0913
        self,
        service: Service,
        start: Annotated[
            Jsonable[m.ListRequestStart] | None,
            Parameter(
                description="Start datetime in UTC to filter events instances.",
            ),
        ] = None,
        end: Annotated[
            Jsonable[m.ListRequestEnd] | None,
            Parameter(
                description="End datetime in UTC to filter events instances.",
            ),
        ] = None,
        limit: Annotated[
            Jsonable[m.ListRequestLimit] | None,
            Parameter(
                description="Maximum number of schedules to return. Default is 10.",
            ),
        ] = None,
        offset: Annotated[
            Jsonable[m.ListRequestOffset] | None,
            Parameter(
                description="Number of schedules to skip.",
            ),
        ] = None,
        where: Annotated[
            Jsonable[m.ListRequestWhere] | None,
            Parameter(
                description="Filter to apply to find events.",
            ),
        ] = None,
        include: Annotated[
            Jsonable[m.ListRequestInclude] | None,
            Parameter(
                description="Relations to include in the response.",
            ),
        ] = None,
        order: Annotated[
            Jsonable[m.ListRequestOrder] | None,
            Parameter(
                description="Order to apply to the results.",
            ),
        ] = None,
    ) -> Response[Serializable[m.ListResponseResults]]:
        """List event schedules with instances between two dates."""
        request = m.ListRequest(
            start=start.root if start else None,
            end=end.root if end else None,
            limit=limit.root if limit else 10,
            offset=offset.root if offset else None,
            where=where.root if where else None,
            include=include.root if include else None,
            order=order.root if order else None,
        )

        try:
            response = await service.list(request)
        except e.ValidationError as ex:
            raise BadRequestException from ex

        return Response(Serializable(response.results))
