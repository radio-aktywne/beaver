from typing import Annotated

from litestar import Controller as BaseController
from litestar import handlers
from litestar.channels import ChannelsPlugin
from litestar.di import Provide
from litestar.params import Parameter
from litestar.response import Response

from emishows.api.exceptions import BadRequestException
from emishows.api.routes.schedule import errors as e
from emishows.api.routes.schedule import models as m
from emishows.api.routes.schedule.service import Service
from emishows.api.validator import Validator
from emishows.services.mevents.service import EventsService
from emishows.state import State


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(
        self,
        state: State,
        channels: ChannelsPlugin,
    ) -> Service:
        return Service(
            events=EventsService(
                datashows=state.datashows,
                datatimes=state.datatimes,
                channels=channels,
            )
        )

    def build(self) -> dict[str, Provide]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the schedules endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.get(
        summary="List schedules",
    )
    async def list(
        self,
        service: Service,
        start: Annotated[
            str | None,
            Parameter(description="Start time in UTC to filter events instances."),
        ] = None,
        end: Annotated[
            str | None,
            Parameter(description="End time in UTC to filter events instances."),
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

        start = Validator(m.ListRequestStart).object(start) if start else None
        end = Validator(m.ListRequestEnd).object(end) if end else None
        where = Validator(m.ListRequestWhere).json(where) if where else None
        include = Validator(m.ListRequestInclude).json(include) if include else None
        order = Validator(m.ListRequestOrder).json(order) if order else None

        req = m.ListRequest(
            start=start,
            end=end,
            limit=limit,
            offset=offset,
            where=where,
            include=include,
            order=order,
        )

        try:
            res = await service.list(req)
        except e.ValidationError as ex:
            raise BadRequestException(extra=str(ex)) from ex

        results = res.results

        return Response(results)
