from litestar import Router

from beaver.api.routes.events.router import router as events_router
from beaver.api.routes.ping.router import router as ping_router
from beaver.api.routes.schedule.router import router as schedule_router
from beaver.api.routes.shows.router import router as shows_router
from beaver.api.routes.sse.router import router as sse_router

router = Router(
    path="/",
    route_handlers=[
        events_router,
        ping_router,
        schedule_router,
        shows_router,
        sse_router,
    ],
)
