from litestar import Router

from emishows.api.routes.events.router import router as events_router
from emishows.api.routes.ping.router import router as ping_router
from emishows.api.routes.schedule.router import router as schedule_router
from emishows.api.routes.shows.router import router as shows_router
from emishows.api.routes.sse.router import router as sse_router

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
