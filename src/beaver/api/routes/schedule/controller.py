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
from beaver.api.validator import Validator
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
                howlite=state.howlite,
                sapphire=state.sapphire,
                channels=channels,
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
            str | None,
            Parameter(description="Start datetime in UTC to filter events instances."),
        ] = None,
        end: Annotated[
            str | None,
            Parameter(description="End datetime in UTC to filter events instances."),
        ] = None,
        limit: Annotated[
            m.ListRequestLimit,
            Parameter(
                description="Maximum number of schedules to return.",
            ),
        ] = 10,
        offset: Annotated[
            m.ListRequestOffset,
            Parameter(
                description="Number of schedules to skip.",
            ),
        ] = None,
        where: Annotated[
            str | None,
            Parameter(
                description="Filter to apply to find events.",
            ),
        ] = None,
        include: Annotated[
            str | None,
            Parameter(
                description="Relations to include in the response.",
            ),
        ] = None,
        order: Annotated[
            str | None,
            Parameter(
                description="Order to apply to the results.",
            ),
        ] = None,
    ) -> Response[m.ListResponseResults]:
        """List event schedules with instances between two dates."""
        parsed_start = (
            Validator[m.ListRequestStart].validate_object(start) if start else None
        )
        parsed_end = Validator[m.ListRequestEnd].validate_object(end) if end else None
        parsed_where = (
            Validator[m.ListRequestWhere].validate_json(where) if where else None
        )
        parsed_include = (
            Validator[m.ListRequestInclude].validate_json(include) if include else None
        )
        parsed_order = (
            Validator[m.ListRequestOrder].validate_json(order) if order else None
        )

        req = m.ListRequest(
            start=parsed_start,
            end=parsed_end,
            limit=limit,
            offset=offset,
            where=parsed_where,
            include=parsed_include,
            order=parsed_order,
        )

        try:
            res = await service.list(req)
        except e.ValidationError as ex:
            raise BadRequestException from ex

        results = res.results

        return Response(results)
