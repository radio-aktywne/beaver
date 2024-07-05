from abc import ABC, abstractmethod
from datetime import timezone
from xml.etree import ElementTree

from emishows.datatimes.models import Query, RecurringQuery, TimeRangeQuery
from emishows.icalendar.parser import ICalendarParser


class QueryBuilder(ABC):
    """Base class for query builders."""

    def get_xml_namespaces(self) -> dict[str, str]:
        """Get XML namespaces."""

        return {
            "D": "DAV:",
            "C": "urn:ietf:params:xml:ns:caldav",
        }

    def _build_prop(self) -> ElementTree.Element:
        """Build prop element."""

        data = ElementTree.Element("C:calendar-data")

        prop = ElementTree.Element("D:prop")
        prop.append(data)

        return prop

    @abstractmethod
    def _build_filters(self) -> list[ElementTree.Element]:
        """Build filter elements."""

        pass

    def _build_filter_root(self) -> ElementTree.Element:
        """Build root filter element."""

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
            attrib={
                f"xmlns:{key}": value
                for key, value in self.get_xml_namespaces().items()
            },
        )

        prop = self._build_prop()
        filter = self._build_filter_root()

        query.append(prop)
        query.append(filter)

        return query


class TimeRangeQueryBuilder(QueryBuilder):
    """Time range query builder."""

    def __init__(self, query: TimeRangeQuery) -> None:
        self._query = query
        self._parser = ICalendarParser()

    def _build_filters(self) -> list[ElementTree.Element]:
        """Build filter elements."""

        attrib = {}

        if self._query.start is not None:
            start = self._query.start.replace(tzinfo=timezone.utc)
            start = self._parser.datetime_to_ical(start)
            start = start.to_ical().decode("utf-8")
            attrib["start"] = start
        if self._query.end is not None:
            end = self._query.end.replace(tzinfo=timezone.utc)
            end = self._parser.datetime_to_ical(end)
            end = end.to_ical().decode("utf-8")
            attrib["end"] = end

        filter = ElementTree.Element("C:time-range", attrib=attrib)

        return [filter]


class RecurringQueryBuilder(QueryBuilder):
    """Recurring query builder."""

    def __init__(self, query: RecurringQuery) -> None:
        self._query = query

    def _build_filters(self) -> list[ElementTree.Element]:
        """Build filter elements."""

        filter = ElementTree.Element("C:prop-filter", name="RRULE")

        if not self._query.recurring:
            filter.append(ElementTree.Element("C:is-not-defined"))

        return [filter]


class QueryBuilderFactory:
    """Query builder factory."""

    class QueryTypeError(TypeError):
        """Query type error."""

        def __init__(self, query: Query) -> None:
            super().__init__(f"Unknown query type: {type(query)}")

    def get(self, query: Query) -> QueryBuilder:
        """Get a query builder."""

        if isinstance(query, TimeRangeQuery):
            return TimeRangeQueryBuilder(query)
        elif isinstance(query, RecurringQuery):
            return RecurringQueryBuilder(query)
        else:
            raise QueryBuilderFactory.QueryTypeError(query)
