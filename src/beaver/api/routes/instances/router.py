from litestar import Router

from beaver.api.routes.instances.controller import Controller

router = Router(
    path="/instances",
    tags=["Instances"],
    route_handlers=[
        Controller,
    ],
)
