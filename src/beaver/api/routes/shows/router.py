from litestar import Router

from beaver.api.routes.shows.controller import Controller

router = Router(
    path="/shows",
    tags=["Shows"],
    route_handlers=[
        Controller,
    ],
)
