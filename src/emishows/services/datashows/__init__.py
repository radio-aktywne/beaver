from typing import TypedDict

from prisma import enums, fields, models, types  # noqa: F401


class StringWithAggregatesFilter(types.StringFilter, total=False):
    _max: types.StringFilter
    _min: types.StringFilter
    _sum: types.StringFilter
    _avg: types.StringFilter
    _count: types.IntFilter


types.StringWithAggregatesFilter = StringWithAggregatesFilter


class DateTimeWithAggregatesFilter(types.DateTimeFilter, total=False):
    _max: types.DateTimeFilter
    _min: types.DateTimeFilter
    _sum: types.DateTimeFilter
    _avg: types.DateTimeFilter
    _count: types.IntFilter


types.DateTimeWithAggregatesFilter = DateTimeWithAggregatesFilter


class BooleanWithAggregatesFilter(types.BooleanFilter, total=False):
    _max: types.BooleanFilter
    _min: types.BooleanFilter
    _sum: types.BooleanFilter
    _avg: types.BooleanFilter
    _count: types.IntFilter


types.BooleanWithAggregatesFilter = BooleanWithAggregatesFilter


class FloatWithAggregatesFilter(types.FloatFilter, total=False):
    _max: types.FloatFilter
    _min: types.FloatFilter
    _sum: types.FloatFilter
    _avg: types.FloatFilter
    _count: types.IntFilter


types.FloatWithAggregatesFilter = FloatWithAggregatesFilter


BytesFilter = TypedDict(
    "BytesFilter",
    {
        "equals": fields.Base64,
        "in": list[fields.Base64],
        "not_in": list[fields.Base64],
        "not": fields.Base64 | types.BytesFilter,
    },
    total=False,
)


types.BytesFilter = BytesFilter


class BytesWithAggregatesFilter(types.BytesFilter, total=False):
    _max: types.BytesFilter
    _min: types.BytesFilter
    _sum: types.BytesFilter
    _avg: types.BytesFilter
    _count: types.IntFilter


types.BytesWithAggregatesFilter = BytesWithAggregatesFilter


JsonFilter = TypedDict(
    "JsonFilter",
    {
        "equals": fields.Json,
        "not": fields.Json,
    },
    total=False,
)


types.JsonFilter = JsonFilter


class JsonWithAggregatesFilter(types.JsonFilter, total=False):
    _max: types.JsonFilter
    _min: types.JsonFilter
    _sum: types.JsonFilter
    _avg: types.JsonFilter
    _count: types.IntFilter


types.JsonWithAggregatesFilter = JsonWithAggregatesFilter


class DecimalWithAggregatesFilter(types.StringFilter, total=False):
    _max: types.DecimalFilter
    _min: types.DecimalFilter
    _sum: types.DecimalFilter
    _avg: types.DecimalFilter
    _count: types.IntFilter


types.DecimalWithAggregatesFilter = DecimalWithAggregatesFilter


class _BytesListFilterEqualsInput(TypedDict):
    equals: list[fields.Base64] | None


types._BytesListFilterEqualsInput = _BytesListFilterEqualsInput


class _BytesListFilterHasInput(TypedDict):
    has: fields.Base64


types._BytesListFilterHasInput = _BytesListFilterHasInput


class _BytesListFilterHasEveryInput(TypedDict):
    has_every: list[fields.Base64]


types._BytesListFilterHasEveryInput = _BytesListFilterHasEveryInput


class _BytesListFilterHasSomeInput(TypedDict):
    has_some: list[fields.Base64]


types._BytesListFilterHasSomeInput = _BytesListFilterHasSomeInput


class _BytesListUpdateSet(TypedDict):
    set: list[fields.Base64]


types._BytesListUpdateSet = _BytesListUpdateSet


BytesListUpdate = list[fields.Base64] | types._BytesListUpdateSet


types.BytesListUpdate = BytesListUpdate


class _JsonListFilterEqualsInput(TypedDict):
    equals: list[fields.Json] | None


types._JsonListFilterEqualsInput = _JsonListFilterEqualsInput


class _JsonListFilterHasInput(TypedDict):
    has: fields.Json


types._JsonListFilterHasInput = _JsonListFilterHasInput


class _JsonListFilterHasEveryInput(TypedDict):
    has_every: list[fields.Json]


types._JsonListFilterHasEveryInput = _JsonListFilterHasEveryInput


class _JsonListFilterHasSomeInput(TypedDict):
    has_some: list[fields.Json]


types._JsonListFilterHasSomeInput = _JsonListFilterHasSomeInput


class _JsonListUpdateSet(TypedDict):
    set: list[fields.Json]


types._JsonListUpdateSet = _JsonListUpdateSet


JsonListUpdate = list[fields.Json] | types._JsonListUpdateSet


class _EventTypeListFilterEqualsInput(TypedDict):
    equals: list[enums.EventType] | None


types._EventTypeListFilterEqualsInput = _EventTypeListFilterEqualsInput


class _EventTypeListFilterHasInput(TypedDict):
    has: enums.EventType


types._EventTypeListFilterHasInput = _EventTypeListFilterHasInput


class _EventTypeListFilterHasEveryInput(TypedDict):
    has_every: list[enums.EventType]


types._EventTypeListFilterHasEveryInput = _EventTypeListFilterHasEveryInput


class _EventTypeListFilterHasSomeInput(TypedDict):
    has_some: list[enums.EventType]


types._EventTypeListFilterHasSomeInput = _EventTypeListFilterHasSomeInput


class _EventTypeListUpdateSet(TypedDict):
    set: list[enums.EventType]


types._EventTypeListUpdateSet = _EventTypeListUpdateSet


EventTypeListUpdate = list[enums.EventType] | types._EventTypeListUpdateSet


class ShowOptionalCreateInput(TypedDict, total=False):
    id: str
    description: str | None
    events: types.EventCreateManyNestedWithoutRelationsInput


types.ShowOptionalCreateInput = ShowOptionalCreateInput


class ShowCreateNestedWithoutRelationsInput(TypedDict, total=False):
    create: types.ShowCreateWithoutRelationsInput
    connect: types.ShowWhereUniqueInput


types.ShowCreateNestedWithoutRelationsInput = ShowCreateNestedWithoutRelationsInput


class ShowCreateManyNestedWithoutRelationsInput(TypedDict, total=False):
    create: (
        types.ShowCreateWithoutRelationsInput
        | list[types.ShowCreateWithoutRelationsInput]
    )
    connect: types.ShowWhereUniqueInput | list[types.ShowWhereUniqueInput]


types.ShowCreateManyNestedWithoutRelationsInput = (
    ShowCreateManyNestedWithoutRelationsInput
)


class ShowUpdateInput(TypedDict, total=False):
    id: str
    title: str
    description: str | None
    events: types.EventUpdateManyWithoutRelationsInput


types.ShowUpdateInput = ShowUpdateInput


class ShowUpdateManyWithoutRelationsInput(TypedDict, total=False):
    create: list[types.ShowCreateWithoutRelationsInput]
    connect: list[types.ShowWhereUniqueInput]
    set: list[types.ShowWhereUniqueInput]
    disconnect: list[types.ShowWhereUniqueInput]
    delete: list[types.ShowWhereUniqueInput]


types.ShowUpdateManyWithoutRelationsInput = ShowUpdateManyWithoutRelationsInput


class ShowUpdateOneWithoutRelationsInput(TypedDict, total=False):
    create: types.ShowCreateWithoutRelationsInput
    connect: types.ShowWhereUniqueInput
    disconnect: bool
    delete: bool


types.ShowUpdateOneWithoutRelationsInput = ShowUpdateOneWithoutRelationsInput


class ShowUpsertInput(TypedDict):
    create: types.ShowCreateInput
    update: types.ShowUpdateInput


types.ShowUpsertInput = ShowUpsertInput


class _ShowIdOrderByInput(TypedDict, total=True):
    id: types.SortOrder


types._Show_id_OrderByInput = _ShowIdOrderByInput


class _ShowTitleOrderByInput(TypedDict, total=True):
    title: types.SortOrder


types._Show_title_OrderByInput = _ShowTitleOrderByInput


class _ShowDescriptionOrderByInput(TypedDict, total=True):
    description: types.SortOrder


types._Show_description_OrderByInput = _ShowDescriptionOrderByInput


ShowOrderByInput = (
    types._Show_id_OrderByInput
    | types._Show_title_OrderByInput
    | types._Show_description_OrderByInput
)


ShowRelationFilter = TypedDict(
    "ShowRelationFilter",
    {
        "is": types.ShowWhereInput,
        "is_not": types.ShowWhereInput,
    },
    total=False,
)


types.ShowRelationFilter = ShowRelationFilter


class ShowListRelationFilter(TypedDict, total=False):
    some: types.ShowWhereInput
    none: types.ShowWhereInput
    every: types.ShowWhereInput


types.ShowListRelationFilter = ShowListRelationFilter


class ShowInclude(TypedDict, total=False):
    events: bool | types.FindManyEventArgsFromShow


types.ShowInclude = ShowInclude


class ShowIncludeFromShow(TypedDict, total=False):
    events: bool | types.FindManyEventArgsFromShow


types.ShowIncludeFromShow = ShowIncludeFromShow


class ShowArgsFromShow(TypedDict, total=False):
    include: types.ShowIncludeFromShow


types.ShowArgsFromShow = ShowArgsFromShow


class FindManyShowArgsFromShow(TypedDict, total=False):
    take: int
    skip: int
    order_by: types.ShowOrderByInput | list[types.ShowOrderByInput]
    where: types.ShowWhereInput
    cursor: types.ShowWhereUniqueInput
    distinct: list[types.ShowScalarFieldKeys]
    include: types.ShowIncludeFromShow


types.FindManyShowArgsFromShow = FindManyShowArgsFromShow


class EventIncludeFromShow(TypedDict, total=False):
    show: bool | types.ShowArgsFromShow


types.EventIncludeFromShow = EventIncludeFromShow


class EventArgsFromShow(TypedDict, total=False):
    include: types.EventIncludeFromEvent


types.EventArgsFromShow = EventArgsFromShow


class FindManyEventArgsFromShow(TypedDict, total=False):
    take: int
    skip: int
    order_by: types.EventOrderByInput | list[types.EventOrderByInput]
    where: types.EventWhereInput
    cursor: types.EventWhereUniqueInput
    distinct: list[types.EventScalarFieldKeys]
    include: types.EventIncludeFromEvent


types.FindManyEventArgsFromShow = FindManyEventArgsFromShow


class ShowWhereInput(TypedDict, total=False):
    id: str | types.StringFilter
    title: str | types.StringFilter
    description: None | str | types.StringFilter
    events: types.EventListRelationFilter
    AND: list[types.ShowWhereInput]
    OR: list[types.ShowWhereInput]
    NOT: list[types.ShowWhereInput]


types.ShowWhereInput = ShowWhereInput


class ShowScalarWhereWithAggregatesInput(TypedDict, total=False):
    id: str | types.StringWithAggregatesFilter
    title: str | types.StringWithAggregatesFilter
    description: str | types.StringWithAggregatesFilter
    AND: list[types.ShowScalarWhereWithAggregatesInput]
    OR: list[types.ShowScalarWhereWithAggregatesInput]
    NOT: list[types.ShowScalarWhereWithAggregatesInput]


types.ShowScalarWhereWithAggregatesInput = ShowScalarWhereWithAggregatesInput


class ShowGroupByOutput(TypedDict, total=False):
    id: str
    title: str
    description: str
    _sum: types.ShowSumAggregateOutput
    _avg: types.ShowAvgAggregateOutput
    _min: types.ShowMinAggregateOutput
    _max: types.ShowMaxAggregateOutput
    _count: types.ShowCountAggregateOutput


types.ShowGroupByOutput = ShowGroupByOutput


class EventOptionalCreateInput(TypedDict, total=False):
    id: str
    showId: str
    show: types.ShowCreateNestedWithoutRelationsInput


types.EventOptionalCreateInput = EventOptionalCreateInput


class EventCreateInput(EventOptionalCreateInput):
    type: enums.EventType


types.EventCreateInput = EventCreateInput


class EventCreateWithoutRelationsInput(types.EventOptionalCreateWithoutRelationsInput):
    type: enums.EventType


types.EventCreateWithoutRelationsInput = EventCreateWithoutRelationsInput


class EventCreateNestedWithoutRelationsInput(TypedDict, total=False):
    create: types.EventCreateWithoutRelationsInput
    connect: types.EventWhereUniqueInput


types.EventCreateNestedWithoutRelationsInput = EventCreateNestedWithoutRelationsInput


class EventCreateManyNestedWithoutRelationsInput(TypedDict, total=False):
    create: (
        types.EventCreateWithoutRelationsInput
        | list[types.EventCreateWithoutRelationsInput]
    )
    connect: types.EventWhereUniqueInput | list[types.EventWhereUniqueInput]


types.EventCreateManyNestedWithoutRelationsInput = (
    EventCreateManyNestedWithoutRelationsInput
)


class EventUpdateInput(TypedDict, total=False):
    id: str
    type: enums.EventType
    show: types.ShowUpdateOneWithoutRelationsInput


types.EventUpdateInput = EventUpdateInput


class EventUpdateManyMutationInput(TypedDict, total=False):
    id: str
    type: enums.EventType


types.EventUpdateManyMutationInput = EventUpdateManyMutationInput


class EventUpdateManyWithoutRelationsInput(TypedDict, total=False):
    create: list[types.EventCreateWithoutRelationsInput]
    connect: list[types.EventWhereUniqueInput]
    set: list[types.EventWhereUniqueInput]
    disconnect: list[types.EventWhereUniqueInput]
    delete: list[types.EventWhereUniqueInput]


types.EventUpdateManyWithoutRelationsInput = EventUpdateManyWithoutRelationsInput


class EventUpdateOneWithoutRelationsInput(TypedDict, total=False):
    create: types.EventCreateWithoutRelationsInput
    connect: types.EventWhereUniqueInput
    disconnect: bool
    delete: bool


types.EventUpdateOneWithoutRelationsInput = EventUpdateOneWithoutRelationsInput


class EventUpsertInput(TypedDict):
    create: types.EventCreateInput
    update: types.EventUpdateInput


types.EventUpsertInput = EventUpsertInput


class _EventIdOrderByInput(TypedDict, total=True):
    id: types.SortOrder


types._Event_id_OrderByInput = _EventIdOrderByInput


class _EventTypeOrderByInput(TypedDict, total=True):
    type: types.SortOrder


types._Event_type_OrderByInput = _EventTypeOrderByInput


class _EventShowIdOrderByInput(TypedDict, total=True):
    showId: types.SortOrder


types._Event_showId_OrderByInput = _EventShowIdOrderByInput


EventOrderByInput = (
    types._Event_id_OrderByInput
    | types._Event_type_OrderByInput
    | types._Event_showId_OrderByInput
)


EventRelationFilter = TypedDict(
    "EventRelationFilter",
    {
        "is": types.EventWhereInput,
        "is_not": types.EventWhereInput,
    },
    total=False,
)


types.EventRelationFilter = EventRelationFilter


class EventListRelationFilter(TypedDict, total=False):
    some: types.EventWhereInput
    none: types.EventWhereInput
    every: types.EventWhereInput


types.EventListRelationFilter = EventListRelationFilter


class EventInclude(TypedDict, total=False):
    show: bool | types.ShowArgsFromEvent


types.EventInclude = EventInclude


class ShowIncludeFromEvent(TypedDict, total=False):
    events: bool | types.FindManyEventArgsFromEvent


types.ShowIncludeFromEvent = ShowIncludeFromEvent


class ShowArgsFromEvent(TypedDict, total=False):
    include: types.ShowIncludeFromShow


types.ShowArgsFromEvent = ShowArgsFromEvent


class FindManyShowArgsFromEvent(TypedDict, total=False):
    take: int
    skip: int
    order_by: types.ShowOrderByInput | list[types.ShowOrderByInput]
    where: types.ShowWhereInput
    cursor: types.ShowWhereUniqueInput
    distinct: list[types.ShowScalarFieldKeys]
    include: types.ShowIncludeFromShow


types.FindManyShowArgsFromEvent = FindManyShowArgsFromEvent


class EventIncludeFromEvent(TypedDict, total=False):
    show: bool | types.ShowArgsFromEvent


types.EventIncludeFromEvent = EventIncludeFromEvent


class EventArgsFromEvent(TypedDict, total=False):
    include: types.EventIncludeFromEvent


types.EventArgsFromEvent = EventArgsFromEvent


class FindManyEventArgsFromEvent(TypedDict, total=False):
    take: int
    skip: int
    order_by: types.EventOrderByInput | list[types.EventOrderByInput]
    where: types.EventWhereInput
    cursor: types.EventWhereUniqueInput
    distinct: list[types.EventScalarFieldKeys]
    include: types.EventIncludeFromEvent


types.FindManyEventArgsFromEvent = FindManyEventArgsFromEvent


class EventWhereInput(TypedDict, total=False):
    id: str | types.StringFilter
    type: enums.EventType
    showId: str | types.StringFilter
    show: types.ShowRelationFilter
    AND: list[types.EventWhereInput]
    OR: list[types.EventWhereInput]
    NOT: list[types.EventWhereInput]


types.EventWhereInput = EventWhereInput


class EventScalarWhereWithAggregatesInput(TypedDict, total=False):
    id: str | types.StringWithAggregatesFilter
    type: enums.EventType
    showId: str | types.StringWithAggregatesFilter
    AND: list[types.EventScalarWhereWithAggregatesInput]
    OR: list[types.EventScalarWhereWithAggregatesInput]
    NOT: list[types.EventScalarWhereWithAggregatesInput]


types.EventScalarWhereWithAggregatesInput = EventScalarWhereWithAggregatesInput


class EventGroupByOutput(TypedDict, total=False):
    id: str
    type: enums.EventType
    showId: str
    _sum: types.EventSumAggregateOutput
    _avg: types.EventAvgAggregateOutput
    _min: types.EventMinAggregateOutput
    _max: types.EventMaxAggregateOutput
    _count: types.EventCountAggregateOutput


types.EventGroupByOutput = EventGroupByOutput


class EventScalarAggregateOutput(TypedDict, total=False):
    id: str
    type: enums.EventType
    showId: str


types.EventScalarAggregateOutput = EventScalarAggregateOutput
