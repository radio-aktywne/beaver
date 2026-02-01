from collections.abc import Generator, Sequence
from contextlib import contextmanager
from datetime import datetime
from uuid import UUID

from beaver.api.routes.schedule import errors as e
from beaver.api.routes.schedule import models as m
from beaver.services.icalendar import models as im
from beaver.services.icalendar.service import ICalendarService
from beaver.services.mevents import errors as ee
from beaver.services.mevents import models as em
from beaver.services.mevents.service import EventsService
from beaver.utils.time import naiveutcnow


class Service:
    """Service for the schedule endpoint."""

    def __init__(self, events: EventsService) -> None:
        self._events = events
        self._icalendar = ICalendarService()

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

    async def _count_events(self, where: m.ListRequestWhere, query: em.Query) -> int:
        count_request = em.CountRequest(
            where=where,
            query=query,
        )

        with self._handle_errors():
            count_response = await self._events.count(count_request)

        return count_response.count

    async def _get_events(  # noqa: PLR0913
        self,
        limit: m.ListRequestLimit,
        offset: m.ListRequestOffset,
        where: m.ListRequestWhere,
        query: em.Query,
        include: m.ListRequestInclude,
        order: m.ListRequestOrder,
    ) -> Sequence[em.Event]:
        list_request = em.ListRequest(
            limit=limit,
            offset=offset,
            where=where,
            query=query,
            include=include,
            order=order,
        )

        with self._handle_errors():
            list_response = await self._events.list(list_request)

        return list_response.events

    def _get_schedule(
        self, event: em.Event, start: datetime, end: datetime
    ) -> m.Schedule:
        ievent = im.Event(
            id=UUID(event.id),
            start=event.start,
            end=event.end,
            timezone=event.timezone,
            recurrence=event.recurrence,
        )

        instances = self._icalendar.expander.expand(ievent, start, end)

        return m.Schedule(
            event=m.Event.map(event),
            instances=[m.EventInstance.map(instance) for instance in instances],
        )

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List schedules."""
        now = naiveutcnow()
        start = request.start if request.start is not None else now
        end = request.end if request.end is not None else now

        query = em.TimeRangeQuery(
            start=start,
            end=end,
        )

        count = await self._count_events(request.where, query)
        events = await self._get_events(
            request.limit,
            request.offset,
            request.where,
            query,
            request.include,
            request.order,
        )
        schedules = [self._get_schedule(event, start, end) for event in events]

        return m.ListResponse(
            results=m.ScheduleList(
                count=count,
                limit=request.limit,
                offset=request.offset,
                schedules=schedules,
            )
        )
