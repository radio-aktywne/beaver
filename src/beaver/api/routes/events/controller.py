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
from beaver.models.base import Jsonable, Serializable
from beaver.services.mevents.service import EventsService
from beaver.state import State


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, state: State, channels: ChannelsPlugin) -> Service:
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
    """Controller for the events endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.get(
        summary="List events",
    )
    async def list(  # noqa: PLR0913
        self,
        service: Service,
        limit: Annotated[
            Jsonable[m.ListRequestLimit] | None,
            Parameter(
                description="Maximum number of events to return. Default is 10.",
            ),
        ] = None,
        offset: Annotated[
            Jsonable[m.ListRequestOffset] | None,
            Parameter(
                description="Number of events to skip.",
            ),
        ] = None,
        where: Annotated[
            Jsonable[m.ListRequestWhere] | None,
            Parameter(
                description="Filter to apply to find events.",
            ),
        ] = None,
        q: Annotated[
            Jsonable[m.ListRequestQuery] | None,
            Parameter(
                description="Advanced query to apply to find events.",
                query="query",
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
        """List events that match the request."""
        request = m.ListRequest(
            limit=limit.root if limit else 10,
            offset=offset.root if offset else None,
            where=where.root if where else None,
            query=q.root if q else None,
            include=include.root if include else None,
            order=order.root if order else None,
        )

        try:
            response = await service.list(request)
        except e.ValidationError as ex:
            raise BadRequestException from ex

        return Response(Serializable(response.results))

    @handlers.get(
        "/{id:str}",
        summary="Get event",
    )
    async def get(
        self,
        service: Service,
        id: Annotated[  # noqa: A002
            Serializable[m.GetRequestId],
            Parameter(
                description="Identifier of the event to get.",
            ),
        ],
        include: Annotated[
            Jsonable[m.GetRequestInclude] | None,
            Parameter(
                description="Relations to include in the response.",
            ),
        ] = None,
    ) -> Response[Serializable[m.GetResponseEvent]]:
        """Get an event by ID."""
        request = m.GetRequest(id=id.root, include=include.root if include else None)

        try:
            response = await service.get(request)
        except e.ValidationError as ex:
            raise BadRequestException from ex
        except e.EventNotFoundError as ex:
            raise NotFoundException from ex

        return Response(Serializable(response.event))

    @handlers.post(
        summary="Create event",
    )
    async def create(
        self,
        service: Service,
        data: Annotated[
            Serializable[m.CreateRequestData],
            Body(
                description="Data to create an event.",
            ),
        ],
        include: Annotated[
            Jsonable[m.CreateRequestInclude] | None,
            Parameter(
                description="Relations to include in the response.",
            ),
        ] = None,
    ) -> Response[Serializable[m.CreateResponseEvent]]:
        """Create a new event."""
        request = m.CreateRequest(
            data=data.root,
            include=include.root if include else None,
        )

        try:
            response = await service.create(request)
        except e.ValidationError as ex:
            raise BadRequestException from ex

        return Response(Serializable(response.event))

    @handlers.patch(
        "/{id:str}",
        summary="Update event",
    )
    async def update(
        self,
        service: Service,
        id: Annotated[  # noqa: A002
            Serializable[m.UpdateRequestId],
            Parameter(
                description="Identifier of the event to update.",
            ),
        ],
        data: Annotated[
            Serializable[m.UpdateRequestData],
            Body(
                description="Data to update an event.",
            ),
        ],
        include: Annotated[
            Jsonable[m.UpdateRequestInclude] | None,
            Parameter(
                description="Relations to include in the response.",
            ),
        ] = None,
    ) -> Response[Serializable[m.UpdateResponseEvent]]:
        """Update an event by ID."""
        request = m.UpdateRequest(
            data=data.root,
            id=id.root,
            include=include.root if include else None,
        )

        try:
            response = await service.update(request)
        except e.ValidationError as ex:
            raise BadRequestException from ex
        except e.EventNotFoundError as ex:
            raise NotFoundException from ex

        return Response(Serializable(response.event))

    @handlers.delete(
        "/{id:str}",
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
            Serializable[m.DeleteRequestId],
            Parameter(
                description="Identifier of the event to delete.",
            ),
        ],
    ) -> Response[None]:
        """Delete an event by ID."""
        request = m.DeleteRequest(id=id.root)

        try:
            await service.delete(request)
        except e.ValidationError as ex:
            raise BadRequestException from ex
        except e.EventNotFoundError as ex:
            raise NotFoundException from ex

        return Response(None)
