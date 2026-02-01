from collections.abc import Generator
from contextlib import contextmanager

from beaver.api.routes.events import errors as e
from beaver.api.routes.events import models as m
from beaver.services.mevents import errors as ee
from beaver.services.mevents import models as em
from beaver.services.mevents.service import EventsService


class Service:
    """Service for the events endpoint."""

    def __init__(self, events: EventsService) -> None:
        self._events = events

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except ee.ValidationError as ex:
            raise e.ValidationError from ex
        except ee.HowliteError as ex:
            raise e.HowliteError from ex
        except ee.SapphireError as ex:
            raise e.SapphireError from ex
        except ee.ServiceError as ex:
            raise e.ServiceError from ex

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List events."""
        count_request = em.CountRequest(
            where=request.where,
            query=request.query.map() if request.query is not None else None,
        )

        with self._handle_errors():
            count_response = await self._events.count(count_request)

        list_request = em.ListRequest(
            limit=request.limit,
            offset=request.offset,
            where=request.where,
            query=request.query.map() if request.query is not None else None,
            include=request.include,
            order=request.order,
        )

        with self._handle_errors():
            list_response = await self._events.list(list_request)

        return m.ListResponse(
            results=m.EventList(
                count=count_response.count,
                limit=request.limit,
                offset=request.offset,
                events=[m.Event.map(event) for event in list_response.events],
            )
        )

    async def get(self, request: m.GetRequest) -> m.GetResponse:
        """Get event."""
        get_request = em.GetRequest(
            where={
                "id": str(request.id),
            },
            include=request.include,
        )

        with self._handle_errors():
            get_response = await self._events.get(get_request)

        if get_response.event is None:
            raise e.EventNotFoundError(request.id)

        return m.GetResponse(event=m.Event.map(get_response.event))

    async def create(self, request: m.CreateRequest) -> m.CreateResponse:
        """Create event."""
        create_request_data: em.EventCreateInput = {
            "type": request.data["type"],
            "start": request.data["start"],
            "end": request.data["end"],
            "timezone": request.data["timezone"],
        }
        if "id" in request.data:
            create_request_data["id"] = request.data["id"]
        if "showId" in request.data:
            create_request_data["showId"] = request.data["showId"]
        if "recurrence" in request.data:
            create_request_data["recurrence"] = (
                request.data["recurrence"].emap()
                if request.data["recurrence"] is not None
                else None
            )

        create_request = em.CreateRequest(
            data=create_request_data,
            include=request.include,
        )

        with self._handle_errors():
            create_response = await self._events.create(create_request)

        return m.CreateResponse(event=m.Event.map(create_response.event))

    async def update(self, request: m.UpdateRequest) -> m.UpdateResponse:
        """Update event."""
        update_request_data: em.EventUpdateInput = {}
        if "id" in request.data:
            update_request_data["id"] = request.data["id"]
        if "type" in request.data:
            update_request_data["type"] = request.data["type"]
        if "start" in request.data:
            update_request_data["start"] = request.data["start"]
        if "end" in request.data:
            update_request_data["end"] = request.data["end"]
        if "timezone" in request.data:
            update_request_data["timezone"] = request.data["timezone"]
        if "recurrence" in request.data:
            update_request_data["recurrence"] = (
                request.data["recurrence"].emap()
                if request.data["recurrence"] is not None
                else None
            )

        update_request = em.UpdateRequest(
            data=update_request_data,
            where={
                "id": str(request.id),
            },
            include=request.include,
        )

        with self._handle_errors():
            update_response = await self._events.update(update_request)

        if update_response.event is None:
            raise e.EventNotFoundError(request.id)

        return m.UpdateResponse(event=m.Event.map(update_response.event))

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete event."""
        delete_request = em.DeleteRequest(
            where={
                "id": str(request.id),
            },
            include=None,
        )

        with self._handle_errors():
            delete_response = await self._events.delete(delete_request)

        if delete_response.event is None:
            raise e.EventNotFoundError(request.id)

        return m.DeleteResponse()
