from uuid import UUID
from xml.etree import ElementTree

from gracy import BaseEndpoint, GracefulRetry, Gracy, GracyConfig
from httpx import BasicAuth

from emishows.config.models import DatatimesConfig
from emishows.datatimes.models import Calendar, Event, Query
from emishows.datatimes.queries import QueryBuilderFactory
from emishows.icalendar.parser import ICalendarParser


class DatatimesEndpoint(BaseEndpoint):
    """Endpoints for datatimes API."""

    CALENDAR = "/"
    EVENT = "/{EVENT}.ics"


class DatatimesServiceBase(Gracy[DatatimesEndpoint]):
    """Base class for datatimes API service."""

    def __init__(self, config: DatatimesConfig, *args, **kwargs) -> None:
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


class DatatimesService(DatatimesServiceBase):
    """Service for datatimes API."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._parser = ICalendarParser()
        self._query_builder_factory = QueryBuilderFactory()

    def _build_auth(self) -> BasicAuth:
        return BasicAuth(
            username=self._config.caldav.user, password=self._config.caldav.password
        )

    def _build_query_payload(self, query: ElementTree.Element) -> str:
        return ElementTree.tostring(query).decode("utf-8")

    def _retrieve_calendars_data_from_query_response(
        self, response: str, namespaces: dict[str, str]
    ) -> list[str]:
        root = ElementTree.fromstring(response)
        calendars = root.findall(".//C:calendar-data", namespaces=namespaces)
        return [calendar.text for calendar in calendars]

    async def get_calendar(self) -> Calendar:
        response = await self.get(DatatimesEndpoint.CALENDAR, auth=self._build_auth())
        return self._parser.string_to_calendar(response.text)

    async def get_event(self, id: UUID) -> Event:
        response = await self.get(
            DatatimesEndpoint.EVENT, {"EVENT": id}, auth=self._build_auth()
        )
        calendar = self._parser.string_to_calendar(response.text)
        return calendar.events[0]

    async def query_events(self, query: Query) -> list[Event]:
        builder = self._query_builder_factory.get(query)

        namespaces = builder.get_xml_namespaces()
        query = builder.build()
        payload = self._build_query_payload(query)

        response = await self._request(
            "REPORT",
            DatatimesEndpoint.CALENDAR,
            auth=self._build_auth(),
            content=payload,
            headers={"Content-Type": "application/xml"},
        )

        data = self._retrieve_calendars_data_from_query_response(
            response.text, namespaces
        )

        calendars = [self._parser.string_to_calendar(d) for d in data]

        return [event for calendar in calendars for event in calendar.events]

    async def upsert_event(self, data: Event) -> Event:
        calendar = Calendar(events=[data])
        payload = self._parser.calendar_to_string(calendar)

        await self.put(
            DatatimesEndpoint.EVENT,
            {"EVENT": data.id},
            auth=self._build_auth(),
            content=payload,
            headers={"Content-Type": "text/calendar"},
        )

        return await self.get_event(data.id)

    async def delete_event(self, id: UUID) -> None:
        await self.delete(
            DatatimesEndpoint.EVENT,
            {"EVENT": id},
            auth=self._build_auth(),
        )
