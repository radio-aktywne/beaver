from collections.abc import Generator
from contextlib import contextmanager

from beaver.api.routes.events import errors as e
from beaver.api.routes.events import models as m
from beaver.services.entities.events import errors as ee
from beaver.services.entities.events import models as em
from beaver.services.entities.events.service import EventsService


class Service:
    """Service for the events endpoint."""

    def __init__(self, events: EventsService) -> None:
        self._events = events

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except ee.ConflictError as ex:
            raise e.ConflictError from ex
        except ee.ValidationError as ex:
            raise e.ValidationError from ex
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
            where={"id": str(request.id)}, include=request.include
        )

        with self._handle_errors():
            get_response = await self._events.get(get_request)

        if get_response.event is None:
            raise e.NotFoundError

        return m.GetResponse(event=m.Event.map(get_response.event))

    def _map_event_create_input(self, data: m.EventCreateInput) -> em.EventCreateInput:
        """Map event create input to internal representation."""
        edata: em.EventCreateInput = {
            "type": data["type"],
            "start": data["start"],
            "duration": data["duration"],
            "timezone": data["timezone"],
        }

        if "id" in data:
            edata["id"] = data["id"]

        if "showId" in data:
            edata["showId"] = data["showId"]

        if "recurrence" in data:
            edata["recurrence"] = (
                data["recurrence"].emap() if data["recurrence"] is not None else None
            )

        if "include" in data:
            edata["include"] = (
                {i.emap() for i in include}
                if (include := data["include"]) is not None
                else None
            )

        if "exclude" in data:
            edata["exclude"] = (
                {e.emap() for e in exclude}
                if (exclude := data["exclude"]) is not None
                else None
            )

        return edata

    async def create(self, request: m.CreateRequest) -> m.CreateResponse:
        """Create event."""
        create_request = em.CreateRequest(
            data=self._map_event_create_input(request.data), include=request.include
        )

        with self._handle_errors():
            create_response = await self._events.create(create_request)

        return m.CreateResponse(event=m.Event.map(create_response.event))

    def _map_recurrence_update_input(  # noqa: C901, PLR0912
        self, data: m.RecurrenceUpdateInput
    ) -> em.RecurrenceUpdateInput:
        """Map recurrence rule update input to internal representation."""
        edata: em.RecurrenceUpdateInput = {}

        if "frequency" in data:
            edata["frequency"] = data["frequency"]

        if "until" in data:
            edata["until"] = data["until"]

        if "count" in data:
            edata["count"] = data["count"]

        if "interval" in data:
            edata["interval"] = data["interval"]

        if "by_seconds" in data:
            edata["by_seconds"] = data["by_seconds"]

        if "by_minutes" in data:
            edata["by_minutes"] = data["by_minutes"]

        if "by_hours" in data:
            edata["by_hours"] = data["by_hours"]

        if "by_weekdays" in data:
            edata["by_weekdays"] = (
                {w.emap() for w in by_weekdays}
                if (by_weekdays := data["by_weekdays"]) is not None
                else None
            )

        if "by_monthdays" in data:
            edata["by_monthdays"] = data["by_monthdays"]

        if "by_yeardays" in data:
            edata["by_yeardays"] = data["by_yeardays"]

        if "by_weeks" in data:
            edata["by_weeks"] = data["by_weeks"]

        if "by_months" in data:
            edata["by_months"] = data["by_months"]

        if "by_set_positions" in data:
            edata["by_set_positions"] = data["by_set_positions"]

        if "week_start" in data:
            edata["week_start"] = data["week_start"]

        return edata

    def _map_event_update_input(self, data: m.EventUpdateInput) -> em.EventUpdateInput:
        """Map event update input to internal representation."""
        edata: em.EventUpdateInput = {}

        if "id" in data:
            edata["id"] = data["id"]

        if "type" in data:
            edata["type"] = data["type"]

        if "start" in data:
            edata["start"] = data["start"]

        if "duration" in data:
            edata["duration"] = data["duration"]

        if "timezone" in data:
            edata["timezone"] = data["timezone"]

        if "recurrence" in data:
            edata["recurrence"] = (
                self._map_recurrence_update_input(data["recurrence"])
                if data["recurrence"] is not None
                else None
            )

        if "include" in data:
            edata["include"] = (
                {i.emap() for i in include}
                if (include := data["include"]) is not None
                else None
            )

        if "exclude" in data:
            edata["exclude"] = (
                {e.emap() for e in exclude}
                if (exclude := data["exclude"]) is not None
                else None
            )

        return edata

    async def update(self, request: m.UpdateRequest) -> m.UpdateResponse:
        """Update event."""
        update_request = em.UpdateRequest(
            data=self._map_event_update_input(request.data),
            where={"id": str(request.id)},
            include=request.include,
        )

        with self._handle_errors():
            update_response = await self._events.update(update_request)

        if update_response.event is None:
            raise e.NotFoundError

        return m.UpdateResponse(event=m.Event.map(update_response.event))

    async def delete(self, request: m.DeleteRequest) -> m.DeleteResponse:
        """Delete event."""
        delete_request = em.DeleteRequest(where={"id": str(request.id)}, include=None)

        with self._handle_errors():
            delete_response = await self._events.delete(delete_request)

        if delete_response.event is None:
            raise e.NotFoundError

        return m.DeleteResponse()
