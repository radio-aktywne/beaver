from xml.etree import ElementTree

from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig
from httpx import BasicAuth

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

    def __init__(self, config: HowliteConfig, *args, **kwargs) -> None:
        class Config:
            BASE_URL = config.caldav.url
            SETTINGS = GracyConfig(
                retry=GracefulRetry(
                    delay=1,
                    max_attempts=3,
                    delay_modifier=2,
                ),
            )

        self.Config = Config

        super().__init__(*args, **kwargs)

        self._config = config


class HowliteService(BaseService):
    """Service for howlite database."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._icalendar = ICalendarService()
        self._query_builder_factory = QueryBuilderFactory()

    def _build_auth(self) -> BasicAuth:
        return BasicAuth(
            username=self._config.caldav.user,
            password=self._config.caldav.password,
        )

    def _build_query_payload(self, query: ElementTree.Element) -> str:
        return ElementTree.tostring(query).decode("utf-8")

    def _retrieve_calendars_data_from_query_response(
        self, response: str, namespaces: dict[str, str]
    ) -> list[str]:
        root = ElementTree.fromstring(response)
        calendars = root.findall(".//C:calendar-data", namespaces=namespaces)
        return [calendar.text for calendar in calendars]

    async def get_calendar(
        self, request: m.GetCalendarRequest
    ) -> m.GetCalendarResponse:
        res = await self.get(
            Endpoint.CALENDAR,
            auth=self._build_auth(),
        )

        calendar = self._icalendar.parser.string_to_calendar(res.text)

        return m.GetCalendarResponse(
            calendar=calendar,
        )

    async def get_event(self, request: m.GetEventRequest) -> m.GetEventResponse:
        id = request.id

        res = await self.get(
            Endpoint.EVENT,
            {"EVENT": id},
            auth=self._build_auth(),
        )

        calendar = self._icalendar.parser.string_to_calendar(res.text)
        event = calendar.events[0]

        return m.GetEventResponse(
            event=event,
        )

    async def query_events(
        self, request: m.QueryEventsRequest
    ) -> m.QueryEventsResponse:
        query = request.query

        builder = self._query_builder_factory.get(query)

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

        data = self._retrieve_calendars_data_from_query_response(
            response.text, namespaces
        )

        calendars = [self._icalendar.parser.string_to_calendar(d) for d in data]
        events = [event for calendar in calendars for event in calendar.events]

        return m.QueryEventsResponse(
            events=events,
        )

    async def upsert_event(
        self, request: m.UpsertEventRequest
    ) -> m.UpsertEventResponse:
        event = request.event

        calendar = m.Calendar(
            events=[event],
        )
        payload = self._icalendar.parser.calendar_to_string(calendar)

        await self.put(
            Endpoint.EVENT,
            {"EVENT": event.id},
            auth=self._build_auth(),
            content=payload,
            headers={"Content-Type": "text/calendar"},
        )

        req = m.GetEventRequest(
            id=event.id,
        )

        res = await self.get_event(req)

        event = res.event

        return m.UpsertEventResponse(
            event=event,
        )

    async def delete_event(
        self, request: m.DeleteEventRequest
    ) -> m.DeleteEventResponse:
        id = request.id

        await self.delete(
            Endpoint.EVENT,
            {"EVENT": id},
            auth=self._build_auth(),
        )

        return m.DeleteEventResponse()
