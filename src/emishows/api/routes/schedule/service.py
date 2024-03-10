from emishows.api.routes.schedule import errors as e
from emishows.api.routes.schedule import models as m
from emishows.events import errors as ee
from emishows.events import models as em
from emishows.events.service import EventsService
from emishows.icalendar import models as im
from emishows.icalendar.expander import EventExpander
from emishows.time import naiveutcnow


class Service:
    """Service for the schedule endpoint."""

    def __init__(self, events: EventsService) -> None:
        self._events = events
        self._expander = EventExpander()

    async def _count_events(self, where: m.ListWhereParameter, query: em.Query) -> int:
        """Count events."""

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

        return response.count

    async def _get_events(
        self,
        limit: m.ListLimitParameter,
        offset: m.ListOffsetParameter,
        where: m.ListWhereParameter,
        query: em.Query,
        include: m.ListIncludeParameter,
        order: m.ListOrderParameter,
    ) -> list[em.Event]:
        """Get events."""

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

        return response.events

    def _get_schedule(
        self, event: em.Event, start: em.NaiveDatetime, end: em.NaiveDatetime
    ) -> m.EventSchedule:
        """Get schedule."""

        ievent = im.Event(
            id=event.id,
            start=event.start,
            end=event.end,
            timezone=event.timezone,
            recurrence=event.recurrence,
        )

        instances = self._expander.expand(ievent, start, end)

        return m.EventSchedule(
            event=event,
            instances=instances,
        )

    async def list(
        self,
        start: m.ListStartParameter,
        end: m.ListEndParameter,
        limit: m.ListLimitParameter,
        offset: m.ListOffsetParameter,
        where: m.ListWhereParameter,
        include: m.ListIncludeParameter,
        order: m.ListOrderParameter,
    ) -> m.ListResponse:
        """List schedules."""

        now = naiveutcnow()
        start = start if start is not None else now
        end = end if end is not None else now

        query = em.TimeRangeQuery(start=start, end=end)

        count = await self._count_events(where, query)
        events = await self._get_events(limit, offset, where, query, include, order)

        schedules = [self._get_schedule(event, start, end) for event in events]

        return m.ListResponse(
            count=count,
            limit=limit,
            offset=offset,
            schedules=schedules,
        )
