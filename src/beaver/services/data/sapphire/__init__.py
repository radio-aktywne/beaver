from typing import ForwardRef, get_args

from prisma import enums, fields, models, types


# Fix Prisma's forward references
for value in vars(types).values():
    for arg in get_args(value):
        if isinstance(arg, ForwardRef) and arg.__forward_module__ is None:
            arg.__forward_module__ = types.__name__


__all__ = [
    "enums",
    "fields",
    "models",
    "types",
]
