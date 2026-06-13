from collections.abc import Generator, Sequence
from contextlib import contextmanager
from datetime import datetime
from uuid import UUID

from beaver.services.icalendar import errors as ie
from beaver.services.icalendar import models as im
from beaver.services.icalendar.service import ICalendarService
from beaver.services.instances import errors as e
from beaver.services.instances import models as m
from beaver.services.mevents import errors as ee
from beaver.services.mevents import models as em
from beaver.services.mevents.service import EventsService


class InstancesService:
    """Service to manage instances."""

    def __init__(self, events: EventsService, icalendar: ICalendarService) -> None:
        self._events = events
        self._icalendar = icalendar

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except ee.ValidationError as ex:
            raise e.ValidationError from ex
        except ie.ValidationError as ex:
            raise e.ValidationError from ex
        except ee.ServiceError as ex:
            raise e.ServiceError from ex
        except ie.ServiceError as ex:
            raise e.ServiceError from ex

    async def _get_events(
        self,
        start: datetime,
        end: datetime,
        where: m.InstanceWhereInput | None,
        include: m.InstanceInclude | None,
    ) -> Sequence[em.Event]:
        list_request = em.ListRequest(
            limit=None,
            offset=None,
            where=where["event"]["is"]
            if where and "event" in where and "is" in where["event"]
            else {"NOT": [where["event"]["is_not"]]}
            if where and "event" in where and "is_not" in where["event"]
            else None,
            query=em.TimeRangeQuery(start=start, end=end),
            include=include["event"]["include"]
            if include
            and "event" in include
            and not isinstance(include["event"], bool)
            and "include" in include["event"]
            else None,
            order=None,
        )

        with self._handle_errors():
            list_response = await self._events.list(list_request)

        return list_response.events

    def _get_event_instances(
        self,
        event: em.Event,
        start: datetime,
        end: datetime,
        include: m.InstanceInclude | None,
    ) -> list[m.Instance]:
        ievent = im.Event(
            id=UUID(event.id),
            start=event.start,
            end=event.end,
            timezone=event.timezone,
            recurrence=event.recurrence,
        )

        with self._handle_errors():
            instances = self._icalendar.expander.expand(ievent, start, end)

        return [
            m.Instance(
                start=instance.start,
                end=instance.end,
                event_id=event.id,
                event=event
                if include and "event" in include and include["event"]
                else None,
            )
            for instance in instances
        ]

    def _sort_instances(
        self, instances: list[m.Instance], order: m.InstanceOrderByInput | None
    ) -> list[m.Instance]:
        if order and "start" in order:
            return sorted(
                instances,
                key=lambda instance: instance.start,
                reverse=order["start"] == "desc",
            )

        if order and "end" in order:
            return sorted(
                instances,
                key=lambda instance: instance.end,
                reverse=order["end"] == "desc",
            )

        return instances

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List all instances."""
        events = await self._get_events(
            request.start, request.end, request.where, request.include
        )
        instances = [
            instance
            for event in events
            for instance in self._get_event_instances(
                event, request.start, request.end, request.include
            )
        ]
        instances = self._sort_instances(instances, request.order)

        return m.ListResponse(instances=instances)
