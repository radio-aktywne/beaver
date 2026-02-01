from collections.abc import Mapping, Sequence
from typing import Any, cast
from xml.etree import ElementTree as ET

from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig
from httpx import BasicAuth, Response

from beaver.config.models import HowliteConfig
from beaver.services.howlite import models as m
from beaver.services.howlite.queries import QueryBuilderFactory
from beaver.services.icalendar.service import ICalendarService


class Endpoint(BaseEndpoint):
    """Endpoints for howlite API."""

    CALENDAR = "/"
    EVENT = "/{EVENT}.ics"


class BaseService(Gracy[Endpoint]):
    """Base class for howlite database service."""

    def __init__(self, config: HowliteConfig, *args: Any, **kwargs: Any) -> None:
        self.Config.BASE_URL = config.caldav.url
        self.Config.SETTINGS = GracyConfig(
            retry=GracefulRetry(
                delay=1,
                max_attempts=3,
                delay_modifier=2,
            ),
        )
        super().__init__(*args, **kwargs)
        self._config = config


class HowliteService(BaseService):
    """Service for howlite database."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._icalendar = ICalendarService()
        self._query_builder_factory = QueryBuilderFactory()

    def _build_auth(self) -> BasicAuth:
        return BasicAuth(
            username=self._config.caldav.user,
            password=self._config.caldav.password,
        )

    def _build_query_payload(self, query: ET.Element) -> str:
        return ET.tostring(query).decode("utf-8")

    def _retrieve_calendars_data_from_query_response(
        self, response: str, namespaces: Mapping[str, str]
    ) -> Sequence[str]:
        root = ET.fromstring(response)  # noqa: S314
        calendars = root.findall(".//C:calendar-data", namespaces=dict(namespaces))
        return [calendar.text for calendar in calendars if calendar.text is not None]

    async def get_calendar(
        self, request: m.GetCalendarRequest
    ) -> m.GetCalendarResponse:
        """Get a calendar."""
        response = await self.get(
            Endpoint.CALENDAR,
            auth=self._build_auth(),
        )

        calendar = self._icalendar.parser.string_to_calendar(response.text)

        return m.GetCalendarResponse(calendar=calendar)

    async def get_event(self, request: m.GetEventRequest) -> m.GetEventResponse:
        """Get an event."""
        response = await self.get(
            Endpoint.EVENT,
            {"EVENT": str(request.id)},
            auth=self._build_auth(),
        )

        calendar = self._icalendar.parser.string_to_calendar(response.text)
        event = calendar.events[0]

        return m.GetEventResponse(event=event)

    async def query_events(
        self, request: m.QueryEventsRequest
    ) -> m.QueryEventsResponse:
        """Query events."""
        builder = self._query_builder_factory.get(request.query)

        namespaces = builder.namespaces
        query = builder.build()
        payload = self._build_query_payload(query)

        response = await self._request(
            "REPORT",
            Endpoint.CALENDAR,
            auth=self._build_auth(),
            content=payload,
            headers={"Content-Type": "application/xml"},
        )
        response = cast("Response", response)

        data = self._retrieve_calendars_data_from_query_response(
            response.text, namespaces
        )

        calendars = [self._icalendar.parser.string_to_calendar(d) for d in data]
        events = [event for calendar in calendars for event in calendar.events]

        return m.QueryEventsResponse(events=events)

    async def upsert_event(
        self, request: m.UpsertEventRequest
    ) -> m.UpsertEventResponse:
        """Upsert an event."""
        calendar = m.Calendar(events=[request.event])
        payload = self._icalendar.parser.calendar_to_string(calendar)

        await self.put(
            Endpoint.EVENT,
            {"EVENT": str(request.event.id)},
            auth=self._build_auth(),
            content=payload,
            headers={"Content-Type": "text/calendar"},
        )

        get_event_request = m.GetEventRequest(id=request.event.id)
        get_event_response = await self.get_event(get_event_request)

        return m.UpsertEventResponse(event=get_event_response.event)

    async def delete_event(
        self, request: m.DeleteEventRequest
    ) -> m.DeleteEventResponse:
        """Delete an event."""
        await self.delete(
            Endpoint.EVENT,
            {"EVENT": str(request.id)},
            auth=self._build_auth(),
        )

        return m.DeleteEventResponse()
