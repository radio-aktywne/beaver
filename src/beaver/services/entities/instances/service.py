from collections.abc import Generator, Sequence
from contextlib import contextmanager
from datetime import UTC, datetime
from uuid import UUID

from beaver.services.entities.events import errors as ee
from beaver.services.entities.events import models as em
from beaver.services.entities.events.service import EventsService
from beaver.services.entities.instances import errors as e
from beaver.services.entities.instances import models as m
from beaver.services.icalendar import errors as ie
from beaver.services.icalendar import models as im
from beaver.services.icalendar.service import ICalendarService


class InstancesService:
    """Service to manage instances."""

    def __init__(self, events: EventsService, icalendar: ICalendarService) -> None:
        self._events = events
        self._icalendar = icalendar

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except ee.ConflictError as ex:
            raise e.ConflictError from ex
        except ee.ValidationError as ex:
            raise e.ValidationError from ex
        except ie.ValidationError as ex:
            raise e.ValidationError from ex
        except ee.ServiceError as ex:
            raise e.ServiceError from ex
        except ie.ServiceError as ex:
            raise e.ServiceError from ex

    async def _list_events(
        self,
        query: em.Query,
        where: em.EventWhereInput | None = None,
        include: em.EventInclude | None = None,
    ) -> Sequence[em.Event]:
        list_request = em.ListRequest(
            limit=None,
            offset=None,
            where=where,
            query=query,
            include=include,
            order=None,
        )

        with self._handle_errors():
            list_response = await self._events.list(list_request)

        return list_response.events

    async def _get_event(
        self,
        where: em.EventWhereUniqueInput,
        include: em.EventInclude | None = None,
    ) -> em.Event | None:
        get_request = em.GetRequest(where=where, include=include)

        with self._handle_errors():
            get_response = await self._events.get(get_request)

        return get_response.event

    def _list_event_instances(
        self, event: em.Event, start: datetime, end: datetime
    ) -> Sequence[im.Instance]:
        ievent = im.Event(
            id=UUID(event.id),
            start=event.start,
            duration=event.duration,
            timezone=event.timezone,
            recurrence=event.recurrence,
        )

        with self._handle_errors():
            return self._icalendar.expander.expand(ievent, start, end)

    def _sort_instances(
        self, instances: list[m.Instance], order: m.InstanceOrderByInput | None
    ) -> list[m.Instance]:
        if order and "start" in order:
            return sorted(
                instances,
                key=lambda instance: instance.start,
                reverse=order["start"] == "desc",
            )

        if order and "duration" in order:
            return sorted(
                instances,
                key=lambda instance: instance.duration,
                reverse=order["duration"] == "desc",
            )

        return instances

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List instances."""
        start = request.start
        end = request.end
        where = request.where
        include = request.include

        events = await self._list_events(
            query=em.TimeRangeQuery(start=start, end=end),
            where=where["event"]["is"]
            if where and "event" in where and "is" in where["event"]
            else {"NOT": [where["event"]["is_not"]]}
            if where and "event" in where and "is_not" in where["event"]
            else None,
            include=include["event"]["include"]
            if include
            and "event" in include
            and not isinstance(include["event"], bool)
            and "include" in include["event"]
            else None,
        )

        instances = [
            m.Instance(
                start=instance.start,
                duration=instance.duration,
                event_id=event.id,
                event=event if include and include.get("event") else None,
            )
            for event in events
            for instance in self._list_event_instances(event, start, end)
        ]
        instances = self._sort_instances(instances, request.order)

        return m.ListResponse(instances=instances)

    async def get(self, request: m.GetRequest) -> m.GetResponse:
        """Get instance."""
        where = request.where
        include = request.include

        event = await self._get_event(
            where={"id": where["event_id"]},
            include=include["event"]["include"]
            if include
            and "event" in include
            and not isinstance(include["event"], bool)
            and "include" in include["event"]
            else None,
        )

        if event is None:
            return m.GetResponse(instance=None)

        utcstart = (
            where["start"]
            .replace(tzinfo=event.timezone)
            .astimezone(UTC)
            .replace(tzinfo=None)
        )
        instances = self._list_event_instances(
            event, utcstart, utcstart + event.duration
        )
        instance = next((i for i in instances if i.start == where["start"]), None)

        if instance is None:
            return m.GetResponse(instance=None)

        return m.GetResponse(
            instance=m.Instance(
                start=instance.start,
                duration=instance.duration,
                event_id=event.id,
                event=event if include and include.get("event") else None,
            )
        )

    async def create(self, request: m.CreateRequest) -> m.CreateResponse:
        """Create instance."""
        data = request.data
        include = request.include

        event = await self._get_event(where={"id": data.event_id})

        if event is None:
            raise e.EventDoesNotExistError(data.event_id)

        utcstart = (
            data.start.replace(tzinfo=event.timezone)
            .astimezone(UTC)
            .replace(tzinfo=None)
        )
        instances = self._list_event_instances(
            event, utcstart, utcstart + event.duration
        )

        if any(instance.start == data.start for instance in instances):
            raise e.InstanceAlreadyExistsError(data.event_id, data.start)

        with self._handle_errors():
            update_request = em.UpdateRequest(
                data={
                    "recurrence": {
                        "include": {em.Inclusion(start=data.start)}
                        | (
                            event.recurrence.include
                            if event.recurrence and event.recurrence.include
                            else set()
                        )
                    }
                },
                where={"id": event.id},
                include=include["event"]["include"]
                if include
                and "event" in include
                and not isinstance(include["event"], bool)
                and "include" in include["event"]
                else None,
            )

            update_response = await self._events.update(update_request)

        event = update_response.event

        if event is None:
            raise e.EventDoesNotExistError(data.event_id)

        instances = self._list_event_instances(
            event, utcstart, utcstart + event.duration
        )
        instance = next(i for i in instances if i.start == data.start)

        return m.CreateResponse(
            instance=m.Instance(
                start=instance.start,
                duration=instance.duration,
                event_id=event.id,
                event=event if include and include.get("event") else None,
            )
        )
