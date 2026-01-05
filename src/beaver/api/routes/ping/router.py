from litestar import Router

from beaver.api.routes.ping.controller import Controller

router = Router(
    path="/ping",
    tags=["Ping"],
    route_handlers=[
        Controller,
    ],
)
