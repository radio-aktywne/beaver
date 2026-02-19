from litestar import Router

from beaver.api.routes.events.router import router as events
from beaver.api.routes.ping.router import router as ping
from beaver.api.routes.schedule.router import router as schedule
from beaver.api.routes.shows.router import router as shows
from beaver.api.routes.sse.router import router as sse
from beaver.api.routes.test.router import router as test

router = Router(
    path="/",
    route_handlers=[
        events,
        ping,
        schedule,
        shows,
        sse,
        test,
    ],
)
