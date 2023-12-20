from typing import Annotated, TypeVar

from litestar import Controller as BaseController
from litestar import delete, get, patch, post
from litestar.channels import ChannelsPlugin
from litestar.di import Provide
from litestar.params import Parameter
from pydantic import Json, TypeAdapter
from pydantic import ValidationError as PydanticValidationError

from emishows.api.exceptions import BadRequestException, NotFoundException
from emishows.api.routes.events.errors import NotFoundError, ValidationError
from emishows.api.routes.events.models import (
    CreateIncludeParameter,
    CreateRequest,
    CreateResponse,
    DeleteIdParameter,
    DeleteResponse,
    GetIdParameter,
    GetIncludeParameter,
    GetResponse,
    ListIncludeParameter,
    ListLimitParameter,
    ListOffsetParameter,
    ListOrderParameter,
    ListQueryParameter,
    ListResponse,
    ListWhereParameter,
    UpdateIdParameter,
    UpdateIncludeParameter,
    UpdateRequest,
    UpdateResponse,
)
from emishows.api.routes.events.service import Service
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
                emitimes=state.emitimes,
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
        summary="List events",
        description="List events that match the request.",
    )
    async def list(
        self,
        service: Service,
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
        q: Annotated[
            str | None,
            Parameter(description="Advanced query to apply to events.", query="query"),
        ] = None,
        include: Annotated[
            str | None,
            Parameter(description="Relations to include with events."),
        ] = None,
        order: Annotated[
            str | None,
            Parameter(description="Order to apply to events."),
        ] = None,
    ) -> ListResponse:
        where = self._validate_json(ListWhereParameter, where) if where else None
        query = self._validate_json(ListQueryParameter, q) if q else None
        include = (
            self._validate_json(ListIncludeParameter, include) if include else None
        )
        order = self._validate_json(ListOrderParameter, order) if order else None

        try:
            return await service.list(
                limit=limit,
                offset=offset,
                where=where,
                query=query,
                include=include,
                order=order,
            )
        except ValidationError as e:
            raise BadRequestException(extra=e.message) from e

    @get(
        "/{id:uuid}",
        summary="Get event",
        description="Get an event by ID.",
    )
    async def get(
        self,
        service: Service,
        id: GetIdParameter,
        include: Annotated[
            str | None,
            Parameter(description="Relations to include with event."),
        ] = None,
    ) -> GetResponse:
        include = self._validate_json(GetIncludeParameter, include) if include else None

        try:
            return await service.get(
                id=id,
                include=include,
            )
        except ValidationError as e:
            raise BadRequestException(extra=e.message) from e
        except NotFoundError as e:
            raise NotFoundException(extra=e.message) from e

    @post(
        summary="Create event",
        description="Create an event.",
    )
    async def create(
        self,
        service: Service,
        data: CreateRequest,
        include: Annotated[
            str | None,
            Parameter(description="Relations to include with event."),
        ] = None,
    ) -> CreateResponse:
        data = self._validate_pydantic(CreateRequest, data)
        include = (
            self._validate_json(CreateIncludeParameter, include) if include else None
        )

        try:
            return await service.create(
                data=data,
                include=include,
            )
        except ValidationError as e:
            raise BadRequestException(extra=e.message) from e

    @patch(
        "/{id:uuid}",
        summary="Update event",
        description="Update an event by ID.",
    )
    async def update(
        self,
        service: Service,
        id: UpdateIdParameter,
        data: UpdateRequest,
        include: Annotated[
            str | None,
            Parameter(description="Relations to include with event."),
        ] = None,
    ) -> UpdateResponse:
        data = self._validate_pydantic(UpdateRequest, data)
        include = (
            self._validate_json(UpdateIncludeParameter, include) if include else None
        )

        try:
            return await service.update(
                id=id,
                data=data,
                include=include,
            )
        except ValidationError as e:
            raise BadRequestException(extra=e.message) from e
        except NotFoundError as e:
            raise NotFoundException(extra=e.message) from e

    @delete(
        "/{id:uuid}",
        summary="Delete event",
        description="Delete an event by ID.",
    )
    async def delete(
        self,
        service: Service,
        id: DeleteIdParameter,
    ) -> DeleteResponse:
        try:
            return await service.delete(
                id=id,
            )
        except ValidationError as e:
            raise BadRequestException(extra=e.message) from e
        except NotFoundError as e:
            raise NotFoundException(extra=e.message) from e
