from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from datetime import UTC
from xml.etree import ElementTree as ET

from beaver.services.howlite import models as m
from beaver.services.icalendar.service import ICalendarService


class QueryBuilder(ABC):
    """Base class for query builders."""

    @property
    def namespaces(self) -> Mapping[str, str]:
        """Get XML namespaces."""
        return {
            "D": "DAV:",
            "C": "urn:ietf:params:xml:ns:caldav",
        }

    def _build_prop(self) -> ET.Element:
        data = ET.Element("C:calendar-data")

        prop = ET.Element("D:prop")
        prop.append(data)

        return prop

    @abstractmethod
    def _build_filters(self) -> Sequence[ET.Element]:
        pass

    def _build_filter_root(self) -> ET.Element:
        queryfilters = self._build_filters()

        eventfilter = ET.Element("C:comp-filter", name="VEVENT")
        for queryfilter in queryfilters:
            eventfilter.append(queryfilter)

        calendarfilter = ET.Element("C:comp-filter", name="VCALENDAR")
        calendarfilter.append(eventfilter)

        root = ET.Element("C:filter")
        root.append(calendarfilter)

        return root

    def build(self) -> ET.Element:
        """Build the query."""
        query = ET.Element(
            "C:calendar-query",
            attrib={f"xmlns:{key}": value for key, value in self.namespaces.items()},
        )

        prop = self._build_prop()
        queryfilter = self._build_filter_root()

        query.append(prop)
        query.append(queryfilter)

        return query


class TimeRangeQueryBuilder(QueryBuilder):
    """Time range query builder."""

    def __init__(self, query: m.TimeRangeQuery) -> None:
        self._query = query
        self._icalendar = ICalendarService()

    def _build_filters(self) -> Sequence[ET.Element]:
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

        queryfilter = ET.Element("C:time-range", attrib=attrib)

        return [queryfilter]


class RecurringQueryBuilder(QueryBuilder):
    """Recurring query builder."""

    def __init__(self, query: m.RecurringQuery) -> None:
        self._query = query

    def _build_filters(self) -> Sequence[ET.Element]:
        queryfilter = ET.Element("C:prop-filter", name="RRULE")

        if not self._query.recurring:
            queryfilter.append(ET.Element("C:is-not-defined"))
        return [queryfilter]


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

        if isinstance(query, m.RecurringQuery):
            return RecurringQueryBuilder(query)

        raise QueryBuilderFactory.QueryTypeError(query)
