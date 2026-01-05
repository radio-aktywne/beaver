from collections.abc import Generator
from contextlib import contextmanager
from zoneinfo import ZoneInfo

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
            raise e.ValidationError(str(ex)) from ex
        except ee.HowliteError as ex:
            raise e.HowliteError(str(ex)) from ex
        except ee.SapphireError as ex:
            raise e.SapphireError(str(ex)) from ex
        except ee.ServiceError as ex:
            raise e.ServiceError(str(ex)) from ex

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List events."""
        limit = request.limit
        offset = request.offset
        where = request.where
        query = request.query
        include = request.include
        order = request.order

        req = em.CountRequest(
            where=where,
            query=query.map() if query is not None else None,
        )

        with self._handle_errors():
            res = await self._events.count(req)

        count = res.count

        req = em.ListRequest(
            limit=limit,
            offset=offset,
            where=where,
            query=query.map() if query is not None else None,
            include=include,
            order=order,
        )

        with self._handle_errors():
            res = await self._events.list(req)

        events = res.events

        events = [m.Event.map(event) for event in events]
        results = m.EventList(
            count=count,
            limit=limit,
            offset=offset,
            events=events,
        )
        return m.ListResponse(
            results=results,
        )

    async def get(self, request: m.GetRequest) -> m.GetResponse:
        """Get event."""
        event_id = request.id
        include = request.include

        req = em.GetRequest(
            where={
                "id": str(event_id),
            },
            include=include,
        )

        with self._handle_errors():
            res = await self._events.get(req)

        event = res.event

        if event is None:
            raise e.EventNotFoundError(event_id)

        event = m.Event.map(event)
        return m.GetResponse(
            event=event,
        )

    async def create(self, request: m.CreateRequest) -> m.CreateResponse:
        """Create event."""
        data = request.data
        include = request.include

        d: em.EventCreateInput = {
            "type": data["type"],
            "start": data["start"],
            "end": data["end"],
            "timezone": ZoneInfo(data["timezone"]),
        }
        if "id" in data:
            d["id"] = data["id"]
        if "showId" in data:
            d["showId"] = data["showId"]
        if "recurrence" in data:
            d["recurrence"] = (
                data["recurrence"].emap() if data["recurrence"] is not None else None
            )

        req = em.CreateRequest(
            data=d,
            include=include,
        )

        with self._handle_errors():
            res = await self._events.create(req)

        event = res.event

        event = m.Event.map(event)
        return m.CreateResponse(
            event=event,
        )

    async def update(self, request: m.UpdateRequest) -> m.UpdateResponse:
        """Update event."""
        data = request.data
        event_id = request.id
        include = request.include

        d: em.EventUpdateInput = {}
        if "id" in data:
            d["id"] = data["id"]
        if "type" in data:
            d["type"] = data["type"]
        if "start" in data:
            d["start"] = data["start"]
        if "end" in data:
            d["end"] = data["end"]
        if "timezone" in data:
            d["timezone"] = ZoneInfo(data["timezone"])
        if "recurrence" in data:
            d["recurrence"] = (
                data["recurrence"].emap() if data["recurrence"] is not None else None
            )

        req = em.UpdateRequest(
            data=d,
            where={
                "id": str(event_id),
            },
            include=include,
        )

        with self._handle_errors():
            res = await self._events.update(req)

        event = res.event

        if event is None:
            raise e.EventNotFoundError(event_id)

        event = m.Event.map(event)
        return m.UpdateResponse(
            event=event,
        )

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete event."""
        event_id = request.id

        req = em.DeleteRequest(
            where={
                "id": str(event_id),
            },
            include=None,
        )

        with self._handle_errors():
            res = await self._events.delete(req)

        event = res.event

        if event is None:
            raise e.EventNotFoundError(event_id)

        return m.DeleteResponse()
