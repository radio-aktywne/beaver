from collections.abc import Mapping
from typing import Annotated

from litestar import Controller as BaseController
from litestar import handlers
from litestar.di import Provide
from litestar.params import Parameter
from litestar.response import Response

from beaver.api.exceptions import BadRequestException, NotFoundException
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
                events=EventsService(howlite=state.howlite, sapphire=state.sapphire),
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
            order=order.root if order else None,
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
        except e.InstanceNotFoundError as ex:
            raise NotFoundException from ex

        return Response(Serializable(response.instance))
