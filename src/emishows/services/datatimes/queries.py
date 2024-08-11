from abc import ABC, abstractmethod
from datetime import UTC
from xml.etree import ElementTree

from emishows.services.datatimes import models as m
from emishows.services.icalendar.service import ICalendarService


class QueryBuilder(ABC):
    """Base class for query builders."""

    @property
    def namespaces(self) -> dict[str, str]:
        """Get XML namespaces."""

        return {
            "D": "DAV:",
            "C": "urn:ietf:params:xml:ns:caldav",
        }

    def _build_prop(self) -> ElementTree.Element:
        data = ElementTree.Element("C:calendar-data")

        prop = ElementTree.Element("D:prop")
        prop.append(data)

        return prop

    @abstractmethod
    def _build_filters(self) -> list[ElementTree.Element]:
        pass

    def _build_filter_root(self) -> ElementTree.Element:
        filters = self._build_filters()

        eventfilter = ElementTree.Element("C:comp-filter", name="VEVENT")
        for filter in filters:
            eventfilter.append(filter)

        calendarfilter = ElementTree.Element("C:comp-filter", name="VCALENDAR")
        calendarfilter.append(eventfilter)

        root = ElementTree.Element("C:filter")
        root.append(calendarfilter)

        return root

    def build(self) -> ElementTree.Element:
        """Build the query."""

        query = ElementTree.Element(
            "C:calendar-query",
            attrib={f"xmlns:{key}": value for key, value in self.namespaces.items()},
        )

        prop = self._build_prop()
        filter = self._build_filter_root()

        query.append(prop)
        query.append(filter)

        return query


class TimeRangeQueryBuilder(QueryBuilder):
    """Time range query builder."""

    def __init__(self, query: m.TimeRangeQuery) -> None:
        self._query = query
        self._icalendar = ICalendarService()

    def _build_filters(self) -> list[ElementTree.Element]:
        attrib = {}

        if self._query.start is not None:
            start = self._query.start.replace(tzinfo=UTC)
            start = self._icalendar.parser.datetime_to_ical(start)
            start = start.to_ical().decode("utf-8")
            attrib["start"] = start

        if self._query.end is not None:
            end = self._query.end.replace(tzinfo=UTC)
            end = self._icalendar.parser.datetime_to_ical(end)
            end = end.to_ical().decode("utf-8")
            attrib["end"] = end

        filter = ElementTree.Element("C:time-range", attrib=attrib)

        return [filter]


class RecurringQueryBuilder(QueryBuilder):
    """Recurring query builder."""

    def __init__(self, query: m.RecurringQuery) -> None:
        self._query = query

    def _build_filters(self) -> list[ElementTree.Element]:
        filter = ElementTree.Element("C:prop-filter", name="RRULE")

        if not self._query.recurring:
            filter.append(ElementTree.Element("C:is-not-defined"))

        return [filter]


class QueryBuilderFactory:
    """Query builder factory."""

    class QueryTypeError(TypeError):
        """Query type error."""

        def __init__(self, query: m.Query) -> None:
            super().__init__(f"Unknown query type: {type(query)}.")

    def get(self, query: m.Query) -> QueryBuilder:
        """Get a query builder."""

        if isinstance(query, m.TimeRangeQuery):
            return TimeRangeQueryBuilder(query)
        elif isinstance(query, m.RecurringQuery):
            return RecurringQueryBuilder(query)
        else:
            raise QueryBuilderFactory.QueryTypeError(query)
