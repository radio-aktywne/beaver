from collections.abc import Mapping
from typing import Annotated

from litestar import Controller as BaseController
from litestar import handlers
from litestar.di import Provide
from litestar.params import Body, Parameter
from litestar.response import Response

from beaver.api.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from beaver.api.routes.instances import errors as e
from beaver.api.routes.instances import models as m
from beaver.api.routes.instances.service import Service
from beaver.models.base import Jsonable, Serializable
from beaver.services.entities.events.service import EventsService
from beaver.services.entities.instances.service import InstancesService
from beaver.services.icalendar.service import ICalendarService
from beaver.state import State
from beaver.utils.time import naiveutcnow


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, state: State) -> Service:
        return Service(
            instances=InstancesService(
                events=EventsService(
                    howlite=state.howlite,
                    icalendar=ICalendarService(),
                    sapphire=state.sapphire,
                ),
                icalendar=ICalendarService(),
            )
        )

    def build(self) -> Mapping[str, Provide]:
        """Build the dependencies."""
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the instances endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.get(
        summary="List instances",
        raises=[BadRequestException],
    )
    async def list(  # noqa: PLR0913
        self,
        service: Service,
        start: Annotated[
            Jsonable[m.ListRequestStart] | None,
            Parameter(
                description="Start datetime in UTC to filter instances. Default is now.",
            ),
        ] = None,
        end: Annotated[
            Jsonable[m.ListRequestEnd] | None,
            Parameter(
                description="End datetime in UTC to filter instances. Default is now.",
            ),
        ] = None,
        where: Annotated[
            Jsonable[m.ListRequestWhere] | None,
            Parameter(
                description="Filter to apply to find instances.",
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
        """List instances."""
        request = m.ListRequest(
            start=start.root if start else naiveutcnow(),
            end=end.root if end else naiveutcnow(),
            where=where.root if where else None,
            include=include.root if include else None,
            order=order.root if order else {"start": "asc"},
        )

        try:
            response = await service.list(request)
        except e.ValidationError as ex:
            raise BadRequestException from ex

        return Response(Serializable(response.results))

    @handlers.get(
        path="/{eventId:str}/{start:str}",
        summary="Get instance",
        raises=[BadRequestException, NotFoundException],
    )
    async def get(
        self,
        service: Service,
        eventId: Annotated[  # noqa: N803
            Serializable[m.GetRequestEventId],
            Parameter(
                description="Identifier of the event that the instance to get belongs to.",
            ),
        ],
        start: Annotated[
            Serializable[m.GetRequestStart],
            Parameter(
                description="Start datetime of the instance to get in event timezone.",
            ),
        ],
        include: Annotated[
            Jsonable[m.GetRequestInclude] | None,
            Parameter(
                description="Relations to include in the response.",
            ),
        ] = None,
    ) -> Response[Serializable[m.GetResponseInstance]]:
        """Get an instance by event ID and start datetime."""
        request = m.GetRequest(
            event_id=eventId.root,
            start=start.root,
            include=include.root if include else None,
        )

        try:
            response = await service.get(request)
        except e.ValidationError as ex:
            raise BadRequestException from ex
        except e.NotFoundError as ex:
            raise NotFoundException from ex

        return Response(Serializable(response.instance))

    @handlers.post(
        summary="Create instance",
        raises=[BadRequestException, ConflictException],
    )
    async def create(
        self,
        service: Service,
        data: Annotated[
            Serializable[m.CreateRequestData],
            Body(
                description="Data to create an instance.",
            ),
        ],
        include: Annotated[
            Jsonable[m.CreateRequestInclude] | None,
            Parameter(
                description="Relations to include in the response.",
            ),
        ] = None,
    ) -> Response[Serializable[m.CreateResponseInstance]]:
        """Create a new instance."""
        request = m.CreateRequest(
            data=data.root,
            include=include.root if include else None,
        )

        try:
            response = await service.create(request)
        except e.ConflictError as ex:
            raise ConflictException from ex
        except e.ValidationError as ex:
            raise BadRequestException from ex

        return Response(Serializable(response.instance))

    @handlers.patch(
        path="/{eventId:str}/{start:str}",
        summary="Update instance",
        raises=[BadRequestException, NotFoundException, ConflictException],
    )
    async def update(
        self,
        service: Service,
        eventId: Annotated[  # noqa: N803
            Serializable[m.UpdateRequestEventId],
            Parameter(
                description="Identifier of the event that the instance to update belongs to.",
            ),
        ],
        start: Annotated[
            Serializable[m.UpdateRequestStart],
            Parameter(
                description="Start datetime of the instance to update in event timezone.",
            ),
        ],
        data: Annotated[
            Serializable[m.UpdateRequestData],
            Body(
                description="Data to update an instance.",
            ),
        ],
        include: Annotated[
            Jsonable[m.UpdateRequestInclude] | None,
            Parameter(
                description="Relations to include in the response.",
            ),
        ] = None,
    ) -> Response[Serializable[m.UpdateResponseInstance]]:
        """Update an instance by event ID and start datetime."""
        request = m.UpdateRequest(
            data=data.root,
            event_id=eventId.root,
            start=start.root,
            include=include.root if include else None,
        )

        try:
            response = await service.update(request)
        except e.ConflictError as ex:
            raise ConflictException from ex
        except e.ValidationError as ex:
            raise BadRequestException from ex
        except e.NotFoundError as ex:
            raise NotFoundException from ex

        return Response(Serializable(response.instance))

    @handlers.delete(
        path="/{eventId:str}/{start:str}",
        summary="Delete instance",
        raises=[BadRequestException, NotFoundException],
    )
    async def delete(
        self,
        service: Service,
        eventId: Annotated[  # noqa: N803
            Serializable[m.DeleteRequestEventId],
            Parameter(
                description="Identifier of the event that the instance to delete belongs to.",
            ),
        ],
        start: Annotated[
            Serializable[m.DeleteRequestStart],
            Parameter(
                description="Start datetime of the instance to delete in event timezone.",
            ),
        ],
    ) -> None:
        """Delete an instance by event ID and start datetime."""
        request = m.DeleteRequest(
            event_id=eventId.root,
            start=start.root,
        )

        try:
            await service.delete(request)
        except e.ValidationError as ex:
            raise BadRequestException from ex
        except e.NotFoundError as ex:
            raise NotFoundException from ex
