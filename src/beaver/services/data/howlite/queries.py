from abc import ABC, abstractmethod
from typing import override

from caldav.search import CalDAVSearcher

from beaver.services.data.howlite import models as m


class QueryBuilder(ABC):
    """Base class for CalDAV query builders."""

    @abstractmethod
    def _build_searcher(self) -> CalDAVSearcher:
        pass

    def build(self) -> str:
        """Build the calendar-query REPORT body."""
        searcher = self._build_searcher()
        query, _ = searcher.build_search_xml_query()
        return str(query)


class TimeRangeQueryBuilder(QueryBuilder):
    """Time range query builder."""

    def __init__(self, query: m.TimeRangeQuery) -> None:
        self._query = query

    @override
    def _build_searcher(self) -> CalDAVSearcher:
        kwargs = {}

        if self._query.start is not None:
            kwargs["start"] = self._query.start

        if self._query.end is not None:
            kwargs["end"] = self._query.end

        return CalDAVSearcher(event=True, expand=False, **kwargs)


class RecurringQueryBuilder(QueryBuilder):
    """Recurring query builder."""

    def __init__(self, query: m.RecurringQuery) -> None:
        self._query = query

    @override
    def _build_searcher(self) -> CalDAVSearcher:
        searcher = CalDAVSearcher(event=True, expand=False)
        searcher.add_property_filter(
            "RRULE", None, operator="def" if self._query.recurring else "undef"
        )
        return searcher


class QueryBuilderFactory:
    """Query builder factory."""

    def get(self, query: m.Query) -> QueryBuilder:
        """Get a builder for the query."""
        if isinstance(query, m.TimeRangeQuery):
            return TimeRangeQueryBuilder(query)

        if isinstance(query, m.RecurringQuery):
            return RecurringQueryBuilder(query)

        raise TypeError(type(query))
