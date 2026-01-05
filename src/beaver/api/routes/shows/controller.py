from collections.abc import Mapping
from typing import Annotated

from litestar import Controller as BaseController
from litestar import handlers
from litestar.channels import ChannelsPlugin
from litestar.di import Provide
from litestar.openapi import ResponseSpec
from litestar.params import Body, Parameter
from litestar.response import Response
from litestar.status_codes import HTTP_204_NO_CONTENT

from beaver.api.exceptions import BadRequestException, NotFoundException
from beaver.api.routes.shows import errors as e
from beaver.api.routes.shows import models as m
from beaver.api.routes.shows.service import Service
from beaver.api.validator import Validator
from beaver.services.shows.service import ShowsService
from beaver.state import State


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(
        self,
        state: State,
        channels: ChannelsPlugin,
    ) -> Service:
        return Service(
            shows=ShowsService(
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
    """Controller for the shows endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.get(
        summary="List shows",
    )
    async def list(  # noqa: PLR0913
        self,
        service: Service,
        limit: Annotated[
            m.ListRequestLimit,
            Parameter(
                description="Maximum number of shows to return.",
            ),
        ] = 10,
        offset: Annotated[
            m.ListRequestOffset,
            Parameter(
                description="Number of shows to skip.",
            ),
        ] = None,
        where: Annotated[
            str | None,
            Parameter(
                description="Filter to apply to find shows.",
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
        """List shows that match the request."""
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

    @handlers.get(
        "/{id:uuid}",
        summary="Get show",
    )
    async def get(
        self,
        service: Service,
        id: Annotated[  # noqa: A002
            m.GetRequestId,
            Parameter(
                description="Identifier of the show to get.",
            ),
        ],
        include: Annotated[
            str | None,
            Parameter(
                description="Relations to include in the response.",
            ),
        ] = None,
    ) -> Response[m.GetResponseShow]:
        """Get a show by ID."""
        parsed_include = (
            Validator[m.GetRequestInclude].validate_json(include) if include else None
        )

        req = m.GetRequest(
            id=id,
            include=parsed_include,
        )

        try:
            res = await service.get(req)
        except e.ValidationError as ex:
            raise BadRequestException from ex
        except e.ShowNotFoundError as ex:
            raise NotFoundException from ex

        show = res.show

        return Response(show)

    @handlers.post(
        summary="Create show",
    )
    async def create(
        self,
        service: Service,
        data: Annotated[
            m.CreateRequestData,
            Body(
                description="Data to create a show.",
            ),
        ],
        include: Annotated[
            str | None,
            Parameter(
                description="Relations to include in the response.",
            ),
        ] = None,
    ) -> Response[m.CreateResponseShow]:
        """Create a new show."""
        parsed_data = Validator[m.CreateRequestData].validate_object(data)
        parsed_include = (
            Validator[m.CreateRequestInclude].validate_json(include)
            if include
            else None
        )

        req = m.CreateRequest(
            data=parsed_data,
            include=parsed_include,
        )

        try:
            res = await service.create(req)
        except e.ValidationError as ex:
            raise BadRequestException from ex

        show = res.show

        return Response(show)

    @handlers.patch(
        "/{id:uuid}",
        summary="Update show",
    )
    async def update(
        self,
        service: Service,
        id: Annotated[  # noqa: A002
            m.UpdateRequestId,
            Parameter(
                description="Identifier of the show to update.",
            ),
        ],
        data: Annotated[
            m.UpdateRequestData,
            Body(
                description="Data to update a show.",
            ),
        ],
        include: Annotated[
            str | None,
            Parameter(
                description="Relations to include in the response.",
            ),
        ] = None,
    ) -> Response[m.UpdateResponseShow]:
        """Update a show by ID."""
        parsed_data = Validator[m.UpdateRequestData].validate_object(data)
        parsed_include = (
            Validator[m.UpdateRequestInclude].validate_json(include)
            if include
            else None
        )

        req = m.UpdateRequest(
            data=parsed_data,
            id=id,
            include=parsed_include,
        )

        try:
            res = await service.update(req)
        except e.ValidationError as ex:
            raise BadRequestException from ex
        except e.ShowNotFoundError as ex:
            raise NotFoundException from ex

        show = res.show

        return Response(show)

    @handlers.delete(
        "/{id:uuid}",
        summary="Delete show",
        responses={
            HTTP_204_NO_CONTENT: ResponseSpec(
                None, description="Request fulfilled, nothing follows"
            )
        },
    )
    async def delete(
        self,
        service: Service,
        id: Annotated[  # noqa: A002
            m.DeleteRequestId,
            Parameter(
                description="Identifier of the show to delete.",
            ),
        ],
    ) -> Response[None]:
        """Delete a show by ID."""
        req = m.DeleteRequest(
            id=id,
        )

        try:
            await service.delete(req)
        except e.ValidationError as ex:
            raise BadRequestException from ex
        except e.ShowNotFoundError as ex:
            raise NotFoundException from ex

        return Response(None)
