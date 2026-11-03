from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID

from beaver.services.consistency.coordination import errors as ce, models as cm
from beaver.services.consistency.coordination.service import CoordinationService
from beaver.services.entities.events import errors as e, models as m
from beaver.services.icalendar import errors as ie, models as im
from beaver.services.icalendar.service import ICalendarService
from beaver.services.persistence.events import errors as pe
from beaver.services.persistence.service import PersistenceService


class EventsService:
    """Service to manage events."""

    def __init__(
        self,
        coordination: CoordinationService,
        icalendar: ICalendarService,
    ) -> None:
        self._coordination = coordination
        self._icalendar = icalendar

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except pe.ConflictError as ex:
            raise e.ConflictError from ex
        except pe.PartialUpdateInsufficientDataError as ex:
            raise e.PartialUpdateInsufficientDataError from ex
        except (ie.ValidationError, pe.ValidationError) as ex:
            raise e.ValidationError from ex
        except (ce.ServiceError, ie.ServiceError, pe.ServiceError) as ex:
            raise e.ServiceError from ex

    @asynccontextmanager
    async def _transaction(
        self, transaction: cm.Transaction | None = None
    ) -> AsyncGenerator[cm.Transaction]:
        with self._handle_errors():
            async with self._coordination.transaction(transaction) as active:
                yield active

    def _recurrence_event(self, event: m.Event) -> im.Event:
        return im.Event(
            id=UUID(event.id),
            start=event.start,
            duration=event.duration,
            timezone=event.timezone,
            recurrence=event.recurrence,
        )

    def _find_split_instance(self, event: m.Event, at: datetime) -> im.Instance | None:
        utc_at = at.replace(tzinfo=event.timezone).astimezone(UTC)
        instances = self._icalendar.expander.expand(
            self._recurrence_event(event), utc_at, utc_at
        )

        return next((instance for instance in instances if instance.start == at), None)

    def _split_create_data(
        self,
        event: m.Event,
        recurrence: m.Recurrence,
        instance: im.Instance,
        update: m.EventUpdateInput | None,
    ) -> m.EventCreateInput:
        update = update or {}
        rec: m.Recurrence | None = recurrence

        if rec.termination and rec.termination.type == "count":
            instances = self._icalendar.expander.expand(
                self._recurrence_event(event),
                event.start.replace(tzinfo=event.timezone).astimezone(UTC),
                instance.start.replace(tzinfo=event.timezone).astimezone(UTC),
            )
            position = sum(item.start < instance.start for item in instances)
            rec = replace(
                rec,
                termination=m.CountTermination(count=rec.termination.count - position),
            )

        if "recurrence" in update:
            rec = (
                replace(rec, **update["recurrence"])
                if update["recurrence"] is not None
                else None
            )

        data: m.EventCreateInput = {
            "showId": event.show_id,
            "type": update.get("type", event.type),
            "start": update.get("start", instance.start),
            "duration": update.get("duration", event.duration),
            "timezone": update.get("timezone", event.timezone),
            "recurrence": rec,
            "include": update.get(
                "include",
                {i for i in event.include if i.start >= instance.start}
                if event.include is not None
                else None,
            ),
            "exclude": update.get(
                "exclude",
                {e for e in event.exclude if e.start >= instance.start}
                if event.exclude is not None
                else None,
            ),
        }
        if "id" in update:
            data["id"] = update["id"]

        return data

    def _split_update_data(
        self, event: m.Event, instance: im.Instance
    ) -> m.EventUpdateInput:
        return {
            "recurrence": {
                "termination": m.UntilTermination(
                    until=instance.start - timedelta(seconds=1)
                )
            },
            "include": {i for i in event.include if i.start < instance.start}
            if event.include is not None
            else None,
            "exclude": {e for e in event.exclude if e.start < instance.start}
            if event.exclude is not None
            else None,
        }

    async def count(
        self, request: m.CountRequest, *, transaction: cm.Transaction | None = None
    ) -> m.CountResponse:
        """Count events."""
        async with self._transaction(transaction) as active:
            persistence = PersistenceService(active)
            count = await persistence.events.count(request.where, request.query)

        return m.CountResponse(count=count)

    async def list(
        self, request: m.ListRequest, *, transaction: cm.Transaction | None = None
    ) -> m.ListResponse:
        """List events."""
        async with self._transaction(transaction) as active:
            persistence = PersistenceService(active)
            events = await persistence.events.list(
                where=request.where,
                query=request.query,
                include=request.include,
                take=request.limit,
                skip=request.offset,
                order=request.order,
            )

        return m.ListResponse(events=events)

    async def get(
        self, request: m.GetRequest, *, transaction: cm.Transaction | None = None
    ) -> m.GetResponse:
        """Get event."""
        async with self._transaction(transaction) as active:
            persistence = PersistenceService(active)
            event = await persistence.events.get(request.where, include=request.include)

        return m.GetResponse(event=event)

    async def create(
        self, request: m.CreateRequest, *, transaction: cm.Transaction | None = None
    ) -> m.CreateResponse:
        """Create event."""
        async with self._transaction(transaction) as active:
            persistence = PersistenceService(active)
            event = await persistence.events.create(
                request.data, include=request.include
            )

        return m.CreateResponse(event=event)

    async def update(
        self, request: m.UpdateRequest, *, transaction: cm.Transaction | None = None
    ) -> m.UpdateResponse:
        """Update event."""
        async with self._transaction(transaction) as active:
            persistence = PersistenceService(active)
            event = await persistence.events.update(
                request.data, where=request.where, include=request.include
            )

        return m.UpdateResponse(event=event)

    async def split(
        self, request: m.SplitRequest, *, transaction: cm.Transaction | None = None
    ) -> m.SplitResponse:
        """Split event."""
        async with self._transaction(transaction) as active:
            persistence = PersistenceService(active)
            event = await persistence.events.get(request.where)
            if event is None:
                return m.SplitResponse(result=None)

            if event.recurrence is None:
                raise e.SplitOneTimeEventError

            instance = self._find_split_instance(event, request.data["at"])
            if instance is None:
                raise e.SplitInstanceMatchError(event.id, request.data["at"])
            if instance.start == event.start:
                raise e.SplitFirstInstanceError(event.id, request.data["at"])

            cdata = self._split_create_data(
                event, event.recurrence, instance, request.data.get("update")
            )
            udata = self._split_update_data(event, instance)
            after = await persistence.events.create(cdata)
            if await persistence.events.update(udata, where={"id": event.id}) is None:
                raise e.MissingSplitEventsError({event.id})

            event_ids = {event.id, after.id}
            events = await persistence.events.list(
                where={"id": {"in": list(event_ids)}}, include=request.include
            )
            by_id = {item.id: item for item in events}
            missing_ids = event_ids - by_id.keys()
            if missing_ids:
                raise e.MissingSplitEventsError(missing_ids)

            result = m.SplitResult(
                before=by_id[event.id],
                after=by_id[after.id],
            )

        return m.SplitResponse(result=result)

    async def delete(
        self, request: m.DeleteRequest, *, transaction: cm.Transaction | None = None
    ) -> m.DeleteResponse:
        """Delete event."""
        async with self._transaction(transaction) as active:
            persistence = PersistenceService(active)
            event = await persistence.events.delete(
                request.where, include=request.include
            )

        return m.DeleteResponse(event=event)
