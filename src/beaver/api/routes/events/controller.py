from typing import Annotated

from litestar import Controller as BaseController
from litestar import handlers
from litestar.channels import ChannelsPlugin
from litestar.di import Provide
from litestar.params import Body, Parameter
from litestar.response import Response

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

    def build(self) -> dict[str, Provide]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the events endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.get(
        summary="List events",
    )
    async def list(
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

        where = Validator(m.ListRequestWhere).json(where) if where else None
        query = Validator(m.Query).json(q) if q else None
        include = Validator(m.ListRequestInclude).json(include) if include else None
        order = Validator(m.ListRequestOrder).json(order) if order else None

        req = m.ListRequest(
            limit=limit,
            offset=offset,
            where=where,
            query=query,
            include=include,
            order=order,
        )

        try:
            res = await service.list(req)
        except e.ValidationError as ex:
            raise BadRequestException(extra=str(ex)) from ex

        results = res.results

        return Response(results)

    @handlers.get(
        "/{id:uuid}",
        summary="Get event",
    )
    async def get(
        self,
        service: Service,
        id: Annotated[
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

        include = Validator(m.GetRequestInclude).json(include) if include else None

        req = m.GetRequest(
            id=id,
            include=include,
        )

        try:
            res = await service.get(req)
        except e.ValidationError as ex:
            raise BadRequestException(extra=str(ex)) from ex
        except e.EventNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex

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

        data = Validator(m.CreateRequestData).object(data)
        include = Validator(m.CreateRequestInclude).json(include) if include else None

        req = m.CreateRequest(
            data=data,
            include=include,
        )

        try:
            res = await service.create(req)
        except e.ValidationError as ex:
            raise BadRequestException(extra=str(ex)) from ex

        event = res.event

        return Response(event)

    @handlers.patch(
        "/{id:uuid}",
        summary="Update event",
    )
    async def update(
        self,
        service: Service,
        id: Annotated[
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

        data = Validator(m.UpdateRequestData).object(data)
        include = Validator(m.UpdateRequestInclude).json(include) if include else None

        req = m.UpdateRequest(
            data=data,
            id=id,
            include=include,
        )

        try:
            res = await service.update(req)
        except e.ValidationError as ex:
            raise BadRequestException(extra=str(ex)) from ex
        except e.EventNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex

        event = res.event

        return Response(event)

    @handlers.delete(
        "/{id:uuid}",
        summary="Delete event",
    )
    async def delete(
        self,
        service: Service,
        id: Annotated[
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
            raise BadRequestException(extra=str(ex)) from ex
        except e.EventNotFoundError as ex:
            raise NotFoundException(extra=str(ex)) from ex

        return Response(None)
