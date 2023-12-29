from typing import Annotated, TypeVar

from litestar import Controller as BaseController
from litestar import delete, get, patch, post
from litestar.channels import ChannelsPlugin
from litestar.di import Provide
from litestar.params import Parameter
from litestar.response import Response
from pydantic import Json, TypeAdapter
from pydantic import ValidationError as PydanticValidationError

from emishows.api.exceptions import BadRequestException, NotFoundException
from emishows.api.routes.shows.errors import NotFoundError, ValidationError
from emishows.api.routes.shows.models import (
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
    ListResponse,
    ListWhereParameter,
    UpdateIdParameter,
    UpdateIncludeParameter,
    UpdateRequest,
    UpdateResponse,
)
from emishows.api.routes.shows.service import Service
from emishows.shows.service import ShowsService
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
            shows=ShowsService(
                prisma=state.prisma,
                channels=channels,
            )
        )

    def build(self) -> dict[str, Provide]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the shows endpoint."""

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
        summary="List shows",
        description="List shows that match the request.",
    )
    async def list(
        self,
        service: Service,
        limit: Annotated[
            ListLimitParameter,
            Parameter(description="Maximum number of shows to return.", default=10),
        ] = 10,
        offset: Annotated[
            ListOffsetParameter,
            Parameter(description="Number of shows to skip."),
        ] = None,
        where: Annotated[
            str | None,
            Parameter(description="Filter to apply to shows."),
        ] = None,
        include: Annotated[
            str | None,
            Parameter(description="Relations to include with shows."),
        ] = None,
        order: Annotated[
            str | None,
            Parameter(description="Order to apply to shows."),
        ] = None,
    ) -> Response[ListResponse]:
        where = self._validate_json(ListWhereParameter, where) if where else None
        include = (
            self._validate_json(ListIncludeParameter, include) if include else None
        )
        order = self._validate_json(ListOrderParameter, order) if order else None

        try:
            response = await service.list(
                limit=limit,
                offset=offset,
                where=where,
                include=include,
                order=order,
            )
        except ValidationError as e:
            raise BadRequestException(extra=e.message) from e

        return Response(response)

    @get(
        "/{id:uuid}",
        summary="Get show",
        description="Get a show by ID.",
    )
    async def get(
        self,
        service: Service,
        id: GetIdParameter,
        include: Annotated[
            str | None,
            Parameter(description="Relations to include with show."),
        ] = None,
    ) -> Response[GetResponse]:
        include = self._validate_json(GetIncludeParameter, include) if include else None

        try:
            response = await service.get(
                id=id,
                include=include,
            )
        except ValidationError as e:
            raise BadRequestException(extra=e.message) from e
        except NotFoundError as e:
            raise NotFoundException(extra=e.message) from e

        return Response(response)

    @post(
        summary="Create show",
        description="Create a show.",
    )
    async def create(
        self,
        service: Service,
        data: CreateRequest,
        include: Annotated[
            str | None,
            Parameter(description="Relations to include with show."),
        ] = None,
    ) -> Response[CreateResponse]:
        data = self._validate_pydantic(CreateRequest, data)
        include = (
            self._validate_json(CreateIncludeParameter, include) if include else None
        )

        try:
            response = await service.create(
                data=data,
                include=include,
            )
        except ValidationError as e:
            raise BadRequestException(extra=e.message) from e

        return Response(response)

    @patch(
        "/{id:uuid}",
        summary="Update show",
        description="Update a show by ID.",
    )
    async def update(
        self,
        service: Service,
        id: UpdateIdParameter,
        data: UpdateRequest,
        include: Annotated[
            str | None,
            Parameter(description="Relations to include with show."),
        ] = None,
    ) -> Response[UpdateResponse]:
        data = self._validate_pydantic(UpdateRequest, data)
        include = (
            self._validate_json(UpdateIncludeParameter, include) if include else None
        )

        try:
            response = await service.update(
                id=id,
                data=data,
                include=include,
            )
        except ValidationError as e:
            raise BadRequestException(extra=e.message) from e
        except NotFoundError as e:
            raise NotFoundException(extra=e.message) from e

        return Response(response)

    @delete(
        "/{id:uuid}",
        summary="Delete show",
        description="Delete a show by ID.",
    )
    async def delete(
        self,
        service: Service,
        id: DeleteIdParameter,
    ) -> Response[DeleteResponse]:
        try:
            response = await service.delete(
                id=id,
            )
        except ValidationError as e:
            raise BadRequestException(extra=e.message) from e
        except NotFoundError as e:
            raise NotFoundException(extra=e.message) from e

        return Response(response)
