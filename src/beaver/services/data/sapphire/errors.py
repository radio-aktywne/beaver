from prisma.errors import DataError, UniqueViolationError
from prisma.errors import PrismaError as ServiceError

__all__ = [
    "DataError",
    "ServiceError",
    "UniqueViolationError",
]
