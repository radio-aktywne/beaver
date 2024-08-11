from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime
from uuid import UUID

from emishows.api.routes.schedule import errors as e
from emishows.api.routes.schedule import models as m
from emishows.services.icalendar import models as im
from emishows.services.icalendar.service import ICalendarService
from emishows.services.mevents import errors as ee
from emishows.services.mevents import models as em
from emishows.services.mevents.service import EventsService
from emishows.utils.time import naiveutcnow


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
            raise e.ValidationError(str(ex)) from ex
        except ee.DatashowsError as ex:
            raise e.DatashowsError(str(ex)) from ex
        except ee.DatatimesError as ex:
            raise e.DatatimesError(str(ex)) from ex
        except ee.ServiceError as ex:
            raise e.ServiceError(str(ex)) from ex

    async def _count_events(self, where: m.ListRequestWhere, query: em.Query) -> int:
        req = em.CountRequest(
            where=where,
            query=query,
        )

        with self._handle_errors():
            res = await self._events.count(req)

        return res.count

    async def _get_events(
        self,
        limit: m.ListRequestLimit,
        offset: m.ListRequestOffset,
        where: m.ListRequestWhere,
        query: em.Query,
        include: m.ListRequestInclude,
        order: m.ListRequestOrder,
    ) -> list[em.Event]:
        req = em.ListRequest(
            limit=limit,
            offset=offset,
            where=where,
            query=query,
            include=include,
            order=order,
        )

        with self._handle_errors():
            res = await self._events.list(req)

        return res.events

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

        event = m.Event.map(event)
        instances = [m.EventInstance.map(instance) for instance in instances]
        return m.Schedule(
            event=event,
            instances=instances,
        )

    async def list(self, request: m.ListRequest) -> m.ListResponse:
        """List schedules."""

        start = request.start
        end = request.end
        limit = request.limit
        offset = request.offset
        where = request.where
        include = request.include
        order = request.order

        now = naiveutcnow()
        start = start if start is not None else now
        end = end if end is not None else now

        query = em.TimeRangeQuery(
            start=start,
            end=end,
        )

        count = await self._count_events(where, query)
        events = await self._get_events(limit, offset, where, query, include, order)

        schedules = [self._get_schedule(event, start, end) for event in events]

        results = m.ScheduleList(
            count=count,
            limit=limit,
            offset=offset,
            schedules=schedules,
        )
        return m.ListResponse(
            results=results,
        )
