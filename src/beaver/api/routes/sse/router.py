from litestar import Router

from beaver.api.routes.sse.controller import Controller

router = Router(
    path="/sse",
    route_handlers=[
        Controller,
    ],
)
