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
from beaver.api.routes.events import errors as e
from beaver.api.routes.events import models as m
from beaver.api.routes.events.service import Service
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
    """Controller for the events endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.get(
        summary="List events",
    )
    async def list(  # noqa: PLR0913
        self,
        service: Service,
        limit: Annotated[
            m.ListRequestLimit,
            Parameter(
                description="Maximum number of events to return.",
            ),
        ] = 10,
        offset: Annotated[
            m.ListRequestOffset,
            Parameter(
                description="Number of events to skip.",
            ),
        ] = None,
        where: Annotated[
            str | None,
            Parameter(
                description="Filter to apply to find events.",
            ),
        ] = None,
        q: Annotated[
            str | None,
            Parameter(
                description="Advanced query to apply to find events.",
                query="query",
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
        """List events that match the request."""
        parsed_where = (
            Validator[m.ListRequestWhere].validate_json(where) if where else None
        )
        parsed_query = Validator[m.Query].validate_json(q) if q else None
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
            query=parsed_query,
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
        summary="Get event",
    )
    async def get(
        self,
        service: Service,
        id: Annotated[  # noqa: A002
            m.GetRequestId,
            Parameter(
                description="Identifier of the event to get.",
            ),
        ],
        include: Annotated[
            str | None,
            Parameter(
                description="Relations to include in the response.",
            ),
        ] = None,
    ) -> Response[m.GetResponseEvent]:
        """Get an event by ID."""
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
        except e.EventNotFoundError as ex:
            raise NotFoundException from ex

        event = res.event

        return Response(event)

    @handlers.post(
        summary="Create event",
    )
    async def create(
        self,
        service: Service,
        data: Annotated[
            m.CreateRequestData,
            Body(
                description="Data to create an event.",
            ),
        ],
        include: Annotated[
            str | None,
            Parameter(
                description="Relations to include in the response.",
            ),
        ] = None,
    ) -> Response[m.CreateResponseEvent]:
        """Create a new event."""
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

        event = res.event

        return Response(event)

    @handlers.patch(
        "/{id:uuid}",
        summary="Update event",
    )
    async def update(
        self,
        service: Service,
        id: Annotated[  # noqa: A002
            m.UpdateRequestId,
            Parameter(
                description="Identifier of the event to update.",
            ),
        ],
        data: Annotated[
            m.UpdateRequestData,
            Body(
                description="Data to update an event.",
            ),
        ],
        include: Annotated[
            str | None,
            Parameter(
                description="Relations to include in the response.",
            ),
        ] = None,
    ) -> Response[m.UpdateResponseEvent]:
        """Update an event by ID."""
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
        except e.EventNotFoundError as ex:
            raise NotFoundException from ex

        event = res.event

        return Response(event)

    @handlers.delete(
        "/{id:uuid}",
        summary="Delete event",
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
                description="Identifier of the event to delete.",
            ),
        ],
    ) -> Response[None]:
        """Delete an event by ID."""
        req = m.DeleteRequest(
            id=id,
        )

        try:
            await service.delete(req)
        except e.ValidationError as ex:
            raise BadRequestException from ex
        except e.EventNotFoundError as ex:
            raise NotFoundException from ex

        return Response(None)
