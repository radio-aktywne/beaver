from litestar import Router

from beaver.api.routes.events.controller import Controller

router = Router(
    path="/events",
    tags=["Events"],
    route_handlers=[
        Controller,
    ],
)
