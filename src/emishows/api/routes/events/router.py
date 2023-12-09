from litestar import Router

from emishows.api.routes.events.controller import Controller

router = Router(
    path="/events",
    route_handlers=[
        Controller,
    ],
)
