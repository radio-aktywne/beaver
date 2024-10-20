from litestar import Router

from beaver.api.routes.events.controller import Controller

router = Router(
    path="/events",
    route_handlers=[
        Controller,
    ],
)
