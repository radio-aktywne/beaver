from collections import OrderedDict
from datetime import UTC, datetime
from typing import Iterable
from uuid import UUID

import icalendar
from icalendar.parser import tzid_from_dt
from icalendar.prop import WEEKDAY_RULE, vDDDLists
from zoneinfo import ZoneInfo

from beaver.services.icalendar import errors as e
from beaver.services.icalendar import models as m


class ICalendarParser:
    """Parser for iCalendar objects."""

    def string_to_ical(self, value: str) -> icalendar.vText:
        """Convert a string to an icalendar.vText object."""

        return icalendar.vText.from_ical(value)

    def ical_to_string(self, vtext: icalendar.vText) -> str:
        """Convert an icalendar.vText object to a string."""

        return str(vtext)

    def int_to_ical(self, value: int) -> icalendar.vInt:
        """Convert an int to an icalendar.vInt object."""

        return icalendar.vInt.from_ical(str(value))

    def ical_to_int(self, vint: icalendar.vInt) -> int:
        """Convert an icalendar.vInt object to an int."""

        return int(vint)

    def ints_to_ical(self, values: list[int]) -> Iterable[icalendar.vInt]:
        """Convert a list of ints to a list of icalendar.vInt objects."""

        return [self.int_to_ical(value) for value in values]

    def ical_to_ints(
        self, vints: icalendar.vInt | Iterable[icalendar.vInt]
    ) -> list[int]:
        """Convert a list of icalendar.vInt objects to a list of ints."""

        if isinstance(vints, icalendar.vInt):
            vints = [vints]

        return [self.ical_to_int(vint) for vint in vints]

    def datetime_to_ical(self, dt: datetime) -> icalendar.vDatetime:
        """Convert a datetime to an icalendar.vDatetime object."""

        tz = tzid_from_dt(dt)

        if tz == "Etc/UTC":
            tz = "UTC"

        fdt = dt.strftime("%Y%m%dT%H%M%S")
        icaldt = icalendar.vDatetime.from_ical(fdt, tz)
        return icalendar.vDatetime(icaldt)

    def ical_to_datetime(self, vdt: icalendar.vDatetime) -> datetime:
        """Convert an icalendar.vDatetime object to a datetime."""

        return vdt.dt

    def datetimes_to_ical(self, dts: list[datetime]) -> vDDDLists:
        """Convert a list of datetimes to a vDDDLists object."""

        tzs = set([tzid_from_dt(dt) for dt in dts])

        if len(tzs) > 1:
            raise e.DifferentTimezonesError()

        tz = tzs.pop()

        if tz == "Etc/UTC":
            tz = "UTC"

        icaldts = [self.datetime_to_ical(dt) for dt in dts]
        icaldts = ",".join([icaldt.to_ical().decode("utf-8") for icaldt in icaldts])
        icaldts = vDDDLists.from_ical(icaldts, tz)
        return vDDDLists(icaldts)

    def ical_to_datetimes(self, vdts: vDDDLists) -> list[datetime]:
        """Convert a vDDDLists object to a list of datetimes."""

        tz = vdts.params.get("TZID")

        icaldts = vdts.to_ical().decode("utf-8")
        icaldts = icaldts.split(",")
        icaldts = [
            icalendar.vDatetime(icalendar.vDatetime.from_ical(icaldt, tz))
            for icaldt in icaldts
        ]
        return [self.ical_to_datetime(icaldt) for icaldt in icaldts]

    def frequency_to_ical(self, frequency: m.Frequency) -> icalendar.vFrequency:
        """Convert a Frequency to an icalendar.vFrequency object."""

        frequency_map = {
            m.Frequency.SECONDLY: "SECONDLY",
            m.Frequency.MINUTELY: "MINUTELY",
            m.Frequency.HOURLY: "HOURLY",
            m.Frequency.DAILY: "DAILY",
            m.Frequency.WEEKLY: "WEEKLY",
            m.Frequency.MONTHLY: "MONTHLY",
            m.Frequency.YEARLY: "YEARLY",
        }

        return icalendar.vFrequency.from_ical(frequency_map[frequency])

    def ical_to_frequency(self, vfrequency: icalendar.vFrequency) -> m.Frequency:
        """Convert an icalendar.vFrequency object to a Frequency."""

        frequency_map = {
            "SECONDLY": m.Frequency.SECONDLY,
            "MINUTELY": m.Frequency.MINUTELY,
            "HOURLY": m.Frequency.HOURLY,
            "DAILY": m.Frequency.DAILY,
            "WEEKLY": m.Frequency.WEEKLY,
            "MONTHLY": m.Frequency.MONTHLY,
            "YEARLY": m.Frequency.YEARLY,
        }

        return frequency_map[vfrequency.to_ical().decode("utf-8")]

    def weekday_to_ical(self, weekday: m.Weekday) -> icalendar.vWeekday:
        """Convert a Weekday to an icalendar.vWeekday object."""

        weekdays_map = {
            m.Weekday.MONDAY: "MO",
            m.Weekday.TUESDAY: "TU",
            m.Weekday.WEDNESDAY: "WE",
            m.Weekday.THURSDAY: "TH",
            m.Weekday.FRIDAY: "FR",
            m.Weekday.SATURDAY: "SA",
            m.Weekday.SUNDAY: "SU",
        }

        return icalendar.vWeekday.from_ical(weekdays_map[weekday])

    def ical_to_weekday(self, vweekday: icalendar.vWeekday) -> m.Weekday:
        """Convert an icalendar.vWeekday object to a Weekday."""

        weekdays_map = {
            "MO": m.Weekday.MONDAY,
            "TU": m.Weekday.TUESDAY,
            "WE": m.Weekday.WEDNESDAY,
            "TH": m.Weekday.THURSDAY,
            "FR": m.Weekday.FRIDAY,
            "SA": m.Weekday.SATURDAY,
            "SU": m.Weekday.SUNDAY,
        }

        match = WEEKDAY_RULE.match(str(vweekday)).groupdict()
        day = match["weekday"]

        return weekdays_map[day]

    def weekday_rules_to_ical(
        self, rules: list[m.WeekdayRule]
    ) -> Iterable[icalendar.vWeekday]:
        """Convert a list of WeekdayRule objects to a list of icalendar.vWeekday objects."""

        results = []

        for rule in rules:
            day = self.weekday_to_ical(rule.day)
            occurrence = rule.occurrence
            if occurrence is not None:
                occurrence = str(occurrence)

            icalweekday = f"{occurrence}{day}" if occurrence is not None else day
            vweekday = icalendar.vWeekday.from_ical(icalweekday)
            results.append(vweekday)

        return results

    def ical_to_weekday_rules(
        self, vweekdays: icalendar.vWeekday | Iterable[icalendar.vWeekday]
    ) -> list[m.WeekdayRule]:
        """Convert a list of icalendar.vWeekday objects to a list of WeekdayRule objects."""

        if isinstance(vweekdays, icalendar.vWeekday):
            vweekdays = [vweekdays]

        results = []

        for weekday in vweekdays:
            day = self.ical_to_weekday(weekday)

            match = WEEKDAY_RULE.match(str(weekday)).groupdict()
            occurrence = match.get("relative") or None
            if occurrence is not None:
                occurrence = int(occurrence)
                if match.get("signal") == "-":
                    occurrence = -occurrence

            rule = m.WeekdayRule(day=day, occurrence=occurrence)
            results.append(rule)

        return results

    def recurrence_rule_to_ical(self, rule: m.RecurrenceRule) -> icalendar.vRecur:
        """Convert a RecurrenceRule object to an icalendar.vRecur object."""

        parts = OrderedDict()
        parts["FREQ"] = self.frequency_to_ical(rule.frequency).to_ical().decode("utf-8")

        if rule.until is not None:
            until = rule.until.replace(tzinfo=UTC)
            parts["UNTIL"] = self.datetime_to_ical(until).to_ical().decode("utf-8")

        if rule.count is not None:
            parts["COUNT"] = self.int_to_ical(rule.count).to_ical().decode("utf-8")

        if rule.interval is not None:
            parts["INTERVAL"] = (
                self.int_to_ical(rule.interval).to_ical().decode("utf-8")
            )

        if rule.by_seconds is not None:
            parts["BYSECOND"] = ",".join(
                [
                    second.to_ical().decode("utf-8")
                    for second in self.ints_to_ical(rule.by_seconds)
                ]
            )

        if rule.by_minutes is not None:
            parts["BYMINUTE"] = ",".join(
                [
                    minute.to_ical().decode("utf-8")
                    for minute in self.ints_to_ical(rule.by_minutes)
                ]
            )

        if rule.by_hours is not None:
            parts["BYHOUR"] = ",".join(
                [
                    hour.to_ical().decode("utf-8")
                    for hour in self.ints_to_ical(rule.by_hours)
                ]
            )

        if rule.by_weekdays is not None:
            parts["BYWEEKDAY"] = ",".join(
                [
                    weekday.to_ical().decode("utf-8")
                    for weekday in self.weekday_rules_to_ical(rule.by_weekdays)
                ]
            )

        if rule.by_monthdays is not None:
            parts["BYMONTHDAY"] = ",".join(
                [
                    monthday.to_ical().decode("utf-8")
                    for monthday in self.ints_to_ical(rule.by_monthdays)
                ]
            )

        if rule.by_yeardays is not None:
            parts["BYYEARDAY"] = ",".join(
                [
                    yearday.to_ical().decode("utf-8")
                    for yearday in self.ints_to_ical(rule.by_yeardays)
                ]
            )

        if rule.by_weeks is not None:
            parts["BYWEEKNO"] = ",".join(
                [
                    week.to_ical().decode("utf-8")
                    for week in self.ints_to_ical(rule.by_weeks)
                ]
            )

        if rule.by_months is not None:
            parts["BYMONTH"] = ",".join(
                [
                    month.to_ical().decode("utf-8")
                    for month in self.ints_to_ical(rule.by_months)
                ]
            )

        if rule.by_set_positions is not None:
            parts["BYSETPOS"] = ",".join(
                [
                    position.to_ical().decode("utf-8")
                    for position in self.ints_to_ical(rule.by_set_positions)
                ]
            )

        if rule.week_start is not None:
            parts["WKST"] = (
                self.weekday_to_ical(rule.week_start).to_ical().decode("utf-8")
            )

        ical = ";".join([f"{key}={value}" for key, value in parts.items()])

        return icalendar.vRecur.from_ical(ical)

    def ical_to_recurrence_rule(self, vrecur: icalendar.vRecur) -> m.RecurrenceRule:
        """Convert an icalendar.vRecur object to a RecurrenceRule object."""

        frequency = self.ical_to_frequency(icalendar.vFrequency(vrecur.get("freq")[0]))

        until = vrecur.get("until")
        if until is not None:
            until = self.ical_to_datetime(icalendar.vDatetime(until[0]))
            until = until.astimezone(UTC).replace(tzinfo=None)

        count = vrecur.get("count")
        if count is not None:
            count = self.ical_to_int(icalendar.vInt(count[0]))

        interval = vrecur.get("interval")
        if interval is not None:
            interval = self.ical_to_int(icalendar.vInt(interval[0]))

        by_seconds = vrecur.get("bysecond")
        if by_seconds is not None:
            by_seconds = [icalendar.vInt(second) for second in by_seconds]
            by_seconds = self.ical_to_ints(by_seconds)

        by_minutes = vrecur.get("byminute")
        if by_minutes is not None:
            by_minutes = [icalendar.vInt(minute) for minute in by_minutes]
            by_minutes = self.ical_to_ints(by_minutes)

        by_hours = vrecur.get("byhour")
        if by_hours is not None:
            by_hours = [icalendar.vInt(hour) for hour in by_hours]
            by_hours = self.ical_to_ints(by_hours)

        by_weekdays = vrecur.get("byweekday")
        if by_weekdays is not None:
            by_weekdays = [icalendar.vWeekday(weekday) for weekday in by_weekdays]
            by_weekdays = self.ical_to_weekday_rules(by_weekdays)

        by_monthdays = vrecur.get("bymonthday")
        if by_monthdays is not None:
            by_monthdays = [icalendar.vInt(monthday) for monthday in by_monthdays]
            by_monthdays = self.ical_to_ints(by_monthdays)

        by_yeardays = vrecur.get("byyearday")
        if by_yeardays is not None:
            by_yeardays = [icalendar.vInt(yearday) for yearday in by_yeardays]
            by_yeardays = self.ical_to_ints(by_yeardays)

        by_weeks = vrecur.get("byweekno")
        if by_weeks is not None:
            by_weeks = [icalendar.vInt(week) for week in by_weeks]
            by_weeks = self.ical_to_ints(by_weeks)

        by_months = vrecur.get("bymonth")
        if by_months is not None:
            by_months = [icalendar.vInt(month) for month in by_months]
            by_months = self.ical_to_ints(by_months)

        by_set_positions = vrecur.get("bysetpos")
        if by_set_positions is not None:
            by_set_positions = [
                icalendar.vInt(position) for position in by_set_positions
            ]
            by_set_positions = self.ical_to_ints(by_set_positions)

        week_start = vrecur.get("wkst")
        if week_start is not None:
            week_start = self.ical_to_weekday(icalendar.vWeekday(week_start[0]))

        return m.RecurrenceRule(
            frequency=frequency,
            until=until,
            count=count,
            interval=interval,
            by_seconds=by_seconds,
            by_minutes=by_minutes,
            by_hours=by_hours,
            by_weekdays=by_weekdays,
            by_monthdays=by_monthdays,
            by_yeardays=by_yeardays,
            by_weeks=by_weeks,
            by_months=by_months,
            by_set_positions=by_set_positions,
            week_start=week_start,
        )

    def event_to_ical(self, event: m.Event) -> icalendar.Event:
        """Convert an Event object to an icalendar.Event object."""

        ical = icalendar.Event()
        ical.add("uid", self.string_to_ical(str(event.id)))

        start = event.start.replace(tzinfo=event.timezone)
        ical.add("dtstart", self.datetime_to_ical(start))

        end = event.end.replace(tzinfo=event.timezone)
        ical.add("dtend", self.datetime_to_ical(end))

        recurrence = event.recurrence
        if recurrence is not None:
            if recurrence.rule is not None:
                ical.add("rrule", self.recurrence_rule_to_ical(recurrence.rule))
            if recurrence.include is not None:
                rdate = [dt.replace(tzinfo=event.timezone) for dt in recurrence.include]
                ical.add("rdate", self.datetimes_to_ical(rdate))
            if recurrence.exclude is not None:
                exdate = [
                    dt.replace(tzinfo=event.timezone) for dt in recurrence.exclude
                ]
                ical.add("exdate", self.datetimes_to_ical(exdate))

        return ical

    def ical_to_event(self, event: icalendar.Event) -> m.Event:
        """Convert an icalendar.Event object to an Event object."""

        id = UUID(self.ical_to_string(event.get("uid")))

        start = event.get("dtstart")
        end = event.get("dtend")

        tz = tzid_from_dt(start.dt)
        tz = ZoneInfo(tz)

        start = self.ical_to_datetime(start)
        start = start.replace(tzinfo=None)

        end = self.ical_to_datetime(end)
        end = end.replace(tzinfo=None)

        rrule = event.get("rrule")
        rdate = event.get("rdate")
        exdate = event.get("exdate")

        if rrule is None and rdate is None and exdate is None:
            recurrence = None
        else:
            rule = self.ical_to_recurrence_rule(rrule) if rrule is not None else None

            include = self.ical_to_datetimes(rdate) if rdate is not None else None
            include = (
                [dt.replace(tzinfo=None) for dt in include]
                if include is not None
                else None
            )

            exclude = self.ical_to_datetimes(exdate) if exdate is not None else None
            exclude = (
                [dt.replace(tzinfo=None) for dt in exclude]
                if exclude is not None
                else None
            )

            recurrence = m.Recurrence(
                rule=rule,
                include=include,
                exclude=exclude,
            )

        return m.Event(
            id=id,
            start=start,
            end=end,
            timezone=tz,
            recurrence=recurrence,
        )

    def calendar_to_ical(self, calendar: m.Calendar) -> icalendar.Calendar:
        """Convert a Calendar object to an icalendar.Calendar object."""

        ical = icalendar.Calendar()

        for event in calendar.events:
            vevent = self.event_to_ical(event)
            ical.add_component(vevent)

        return ical

    def ical_to_calendar(self, calendar: icalendar.Calendar) -> m.Calendar:
        """Convert an icalendar.Calendar object to a Calendar object."""

        events = [
            self.ical_to_event(event) for event in calendar.walk(icalendar.Event.name)
        ]
        return m.Calendar(events=events)

    def string_to_calendar(self, value: str) -> m.Calendar:
        """Convert a string to a Calendar object."""

        calendar = icalendar.Calendar.from_ical(value)
        return self.ical_to_calendar(calendar)

    def calendar_to_string(self, calendar: m.Calendar) -> str:
        """Convert a Calendar object to a string."""

        ical = self.calendar_to_ical(calendar)
        return ical.to_ical().decode("utf-8")
