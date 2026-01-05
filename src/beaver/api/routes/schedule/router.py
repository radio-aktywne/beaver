from litestar import Router

from beaver.api.routes.schedule.controller import Controller

router = Router(
    path="/schedule",
    tags=["Schedule"],
    route_handlers=[
        Controller,
    ],
)
