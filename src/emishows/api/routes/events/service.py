from emishows.api.routes.events import errors as e
from emishows.api.routes.events import models as m
from emishows.events import errors as ee
from emishows.events import models as em
from emishows.events.service import EventsService


class Service:
    """Service for the events endpoint."""

    def __init__(self, events: EventsService) -> None:
        self._events = events

    async def list(
        self,
        limit: m.ListLimitParameter,
        offset: m.ListOffsetParameter,
        where: m.ListWhereParameter,
        query: m.ListQueryParameter,
        include: m.ListIncludeParameter,
        order: m.ListOrderParameter,
    ) -> m.ListResponse:
        """List events."""

        request = em.CountRequest(
            where=where,
            query=query,
        )

        try:
            response = await self._events.count(request)
        except ee.ValidationError as error:
            raise e.ValidationError(error.message) from error
        except ee.DatabaseError as error:
            raise e.DatabaseError(error.message) from error
        except ee.EmitimesError as error:
            raise e.EmitimesError(error.message) from error
        except ee.ServiceError as error:
            raise e.ServiceError(error.message) from error

        count = response.count

        request = em.ListRequest(
            limit=limit,
            offset=offset,
            where=where,
            query=query,
            include=include,
            order=order,
        )

        try:
            response = await self._events.list(request)
        except ee.ValidationError as error:
            raise e.ValidationError(error.message) from error
        except ee.DatabaseError as error:
            raise e.DatabaseError(error.message) from error
        except ee.EmitimesError as error:
            raise e.EmitimesError(error.message) from error
        except ee.ServiceError as error:
            raise e.ServiceError(error.message) from error

        return m.ListResponse(
            count=count,
            limit=limit,
            offset=offset,
            events=response.events,
        )

    async def get(
        self,
        id: m.GetIdParameter,
        include: m.GetIncludeParameter,
    ) -> m.GetResponse:
        """Get an event."""

        request = em.GetRequest(
            where={"id": str(id)},
            include=include,
        )

        try:
            response = await self._events.get(request)
        except ee.ValidationError as error:
            raise e.ValidationError(error.message) from error
        except ee.DatabaseError as error:
            raise e.DatabaseError(error.message) from error
        except ee.EmitimesError as error:
            raise e.EmitimesError(error.message) from error
        except ee.ServiceError as error:
            raise e.ServiceError(error.message) from error

        event = response.event

        if event is None:
            raise e.NotFoundError()

        return event

    async def create(
        self,
        data: m.CreateRequest,
        include: m.CreateIncludeParameter,
    ) -> m.CreateResponse:
        """Create an event."""

        request = em.CreateRequest(
            data=data,
            include=include,
        )

        try:
            response = await self._events.create(request)
        except ee.ValidationError as error:
            raise e.ValidationError(error.message) from error
        except ee.DatabaseError as error:
            raise e.DatabaseError(error.message) from error
        except ee.EmitimesError as error:
            raise e.EmitimesError(error.message) from error
        except ee.ServiceError as error:
            raise e.ServiceError(error.message) from error

        return response.event

    async def update(
        self,
        id: m.UpdateIdParameter,
        data: m.UpdateRequest,
        include: m.UpdateIncludeParameter,
    ) -> m.UpdateResponse:
        """Update an event."""

        request = em.UpdateRequest(
            data=data,
            where={"id": str(id)},
            include=include,
        )

        try:
            response = await self._events.update(request)
        except ee.ValidationError as error:
            raise e.ValidationError(error.message) from error
        except ee.DatabaseError as error:
            raise e.DatabaseError(error.message) from error
        except ee.EmitimesError as error:
            raise e.EmitimesError(error.message) from error
        except ee.ServiceError as error:
            raise e.ServiceError(error.message) from error

        event = response.event

        if event is None:
            raise e.NotFoundError()

        return event

    async def delete(
        self,
        id: m.DeleteIdParameter,
    ) -> m.DeleteResponse:
        """Delete an event."""

        request = em.DeleteRequest(
            where={"id": str(id)},
        )

        try:
            response = await self._events.delete(request)
        except ee.ValidationError as error:
            raise e.ValidationError(error.message) from error
        except ee.DatabaseError as error:
            raise e.DatabaseError(error.message) from error
        except ee.EmitimesError as error:
            raise e.EmitimesError(error.message) from error
        except ee.ServiceError as error:
            raise e.ServiceError(error.message) from error

        event = response.event

        if event is None:
            raise e.NotFoundError()

        return None
