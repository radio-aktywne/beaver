from collections.abc import AsyncGenerator, Awaitable
from contextlib import asynccontextmanager
from http import HTTPStatus
from uuid import UUID

from caldav import aio
from caldav.elements import dav
from caldav.lib import error as ce

from beaver.config.models import HowliteConfig
from beaver.services.data.howlite import errors as e, models as m
from beaver.services.data.howlite.queries import QueryBuilderFactory
from beaver.services.icalendar import errors as ie
from beaver.services.icalendar.service import ICalendarService


class HowliteService:
    """Service for howlite API."""

    def __init__(self, config: HowliteConfig) -> None:
        self.config = config
        self.icalendar = ICalendarService()
        self.query_builder_factory = QueryBuilderFactory()

    @asynccontextmanager
    async def _client(self) -> AsyncGenerator[aio.AsyncDAVClient]:
        try:
            async with aio.AsyncDAVClient(
                url=self.config.caldav.url,
                username=self.config.caldav.user,
                password=self.config.caldav.password,
                auth_type="basic",
            ) as client:
                yield client
        except (ce.DAVError, ie.ServiceError, OSError, SyntaxError, ValueError) as ex:
            raise e.ServiceError from ex

    def _check_status(self, status: int, *, expected: set[HTTPStatus]) -> None:
        match status:
            case _ if status not in expected:
                raise e.UnexpectedStatusError(status)
            case HTTPStatus.NOT_FOUND:
                raise e.NotFoundError

    async def _request(
        self,
        request: Awaitable[aio.DAVResponse],
        *,
        expected: set[HTTPStatus],
    ) -> aio.DAVResponse:
        response = await request
        self._check_status(response.status, expected=expected)

        return response

    async def get_calendar(
        self, request: m.GetCalendarRequest
    ) -> m.GetCalendarResponse:
        """Get calendar."""
        async with self._client() as client:
            response = await self._request(
                client.request(self.config.caldav.url),
                expected={HTTPStatus.OK},
            )

            calendar = self.icalendar.parser.string_to_calendar(response.raw)

        return m.GetCalendarResponse(calendar=calendar)

    async def get_event(self, request: m.GetEventRequest) -> m.GetEventResponse:
        """Get event."""
        async with self._client() as client:
            response = await self._request(
                client.request(f"{self.config.caldav.url}/{request.id}.ics"),
                expected={HTTPStatus.OK, HTTPStatus.NOT_FOUND},
            )

            calendar = self.icalendar.parser.string_to_calendar(response.raw)
            event = calendar.events[0]

        return m.GetEventResponse(event=event)

    async def list_events(self, request: m.ListEventsRequest) -> m.ListEventsResponse:
        """List event identifiers without downloading calendar data."""
        async with self._client() as client:
            response = await self._request(
                client.propfind(
                    self.config.caldav.url, depth=1, props=["resourcetype"]
                ),
                expected={HTTPStatus.OK, HTTPStatus.MULTI_STATUS},
            )

            resources = response.parse_propfind()
            if not resources:
                raise e.IncompleteCalendarListingError

            ids = set()
            for resource in resources:
                self._check_status(resource.status, expected={HTTPStatus.OK})

                if dav.ResourceType.tag not in resource.properties:
                    raise e.MissingCalendarResourceTypeError

                if dav.Collection.tag in (
                    resource.properties[dav.ResourceType.tag] or []
                ):
                    continue

                name = resource.href.rsplit("/", 1)[-1]
                if name.endswith(".ics"):
                    ids.add(UUID(name.removesuffix(".ics")))

        return m.ListEventsResponse(ids=ids)

    async def query_events(
        self, request: m.QueryEventsRequest
    ) -> m.QueryEventsResponse:
        """Query events."""
        async with self._client() as client:
            try:
                builder = self.query_builder_factory.get(request.query)
            except TypeError as ex:
                raise e.UnknownQueryTypeError(type(request.query)) from ex

            content = builder.build()

            response = await self._request(
                client.report(self.config.caldav.url, body=content, depth=1),
                expected={HTTPStatus.OK, HTTPStatus.MULTI_STATUS},
            )

            if response.tree is None:
                raise e.MissingQueryResponseBodyError

            events = []
            for resource in response.parse_calendar_query():
                self._check_status(resource.status, expected={HTTPStatus.OK})

                if resource.calendar_data is None:
                    raise e.MissingCalendarDataError

                calendar = self.icalendar.parser.string_to_calendar(
                    resource.calendar_data
                )
                events.extend(calendar.events)

        return m.QueryEventsResponse(events=events)

    async def upsert_event(
        self, request: m.UpsertEventRequest
    ) -> m.UpsertEventResponse:
        """Upsert event."""
        calendar = m.Calendar(events=[request.event])
        content = self.icalendar.parser.calendar_to_string(calendar)
        url = f"{self.config.caldav.url}/{request.event.id}.ics"

        async with self._client() as client:
            await self._request(
                client.put(url, content, headers={"Content-Type": "text/calendar"}),
                expected={HTTPStatus.CREATED, HTTPStatus.NO_CONTENT},
            )

            response = await self._request(
                client.request(url), expected={HTTPStatus.OK}
            )

            calendar = self.icalendar.parser.string_to_calendar(response.raw)
            event = calendar.events[0]

        return m.UpsertEventResponse(event=event)

    async def delete_event(
        self, request: m.DeleteEventRequest
    ) -> m.DeleteEventResponse:
        """Delete event."""
        async with self._client() as client:
            await self._request(
                client.delete(f"{self.config.caldav.url}/{request.id}.ics"),
                expected={HTTPStatus.OK, HTTPStatus.NO_CONTENT, HTTPStatus.NOT_FOUND},
            )

        return m.DeleteEventResponse()
