from typing import Annotated, TypeVar

from litestar import Controller as BaseController
from litestar import get
from litestar.channels import ChannelsPlugin
from litestar.di import Provide
from litestar.params import Parameter
from litestar.response import Response
from pydantic import Json, TypeAdapter
from pydantic import ValidationError as PydanticValidationError

from emishows.api.exceptions import BadRequestException
from emishows.api.routes.schedule.errors import ValidationError
from emishows.api.routes.schedule.models import (
    ListEndParameter,
    ListIncludeParameter,
    ListLimitParameter,
    ListOffsetParameter,
    ListOrderParameter,
    ListResponse,
    ListStartParameter,
    ListWhereParameter,
)
from emishows.api.routes.schedule.service import Service
from emishows.events.service import EventsService
from emishows.state import State

T = TypeVar("T")


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(
        self,
        state: State,
        channels: ChannelsPlugin,
    ) -> Service:
        return Service(
            events=EventsService(
                prisma=state.prisma,
                datatimes=state.datatimes,
                channels=channels,
            )
        )

    def build(self) -> dict[str, Provide]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the events endpoint."""

    dependencies = DependenciesBuilder().build()

    def _validate_pydantic(self, t: type[T], v: str) -> T:
        try:
            return TypeAdapter(t).validate_python(v)
        except PydanticValidationError as e:
            raise BadRequestException(extra=e.errors(include_context=False)) from e

    def _validate_json(self, t: type[T], v: str) -> T:
        try:
            return TypeAdapter(Json[t]).validate_strings(v)
        except PydanticValidationError as e:
            raise BadRequestException(extra=e.errors(include_context=False)) from e

    @get(
        summary="List schedules",
        description="List event schedules with instances between two dates.",
    )
    async def list(
        self,
        service: Service,
        start: Annotated[
            str | None,
            Parameter(
                description="Start time in UTC of the event instances to return. By default, the current datetime."
            ),
        ] = None,
        end: Annotated[
            str | None,
            Parameter(
                description="End time in UTC of the event instances to return. By default, the current datetime."
            ),
        ] = None,
        limit: Annotated[
            ListLimitParameter,
            Parameter(description="Maximum number of events to return.", default=10),
        ] = 10,
        offset: Annotated[
            ListOffsetParameter,
            Parameter(description="Number of events to skip."),
        ] = None,
        where: Annotated[
            str | None,
            Parameter(description="Filter to apply to events."),
        ] = None,
        include: Annotated[
            str | None,
            Parameter(description="Relations to include with events."),
        ] = None,
        order: Annotated[
            str | None,
            Parameter(description="Order to apply to events."),
        ] = None,
    ) -> Response[ListResponse]:
        start = self._validate_pydantic(ListStartParameter, start) if start else None
        end = self._validate_pydantic(ListEndParameter, end) if end else None
        where = self._validate_json(ListWhereParameter, where) if where else None
        include = (
            self._validate_json(ListIncludeParameter, include) if include else None
        )
        order = self._validate_json(ListOrderParameter, order) if order else None

        try:
            response = await service.list(
                start=start,
                end=end,
                limit=limit,
                offset=offset,
                where=where,
                include=include,
                order=order,
            )
        except ValidationError as e:
            raise BadRequestException(extra=e.message) from e

        return Response(response)
