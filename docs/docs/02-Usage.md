---
slug: /usage
title: Usage
---

## Managing shows, events and instances

You can manage shows, events and instances using
the `/shows`, `/events` and `/instances` endpoints.
The API follows RESTful conventions,
so you can use the following HTTP methods wherever applicable:

- `GET` to retrieve a resource or a list of resources
- `POST` to create a new resource
- `PATCH` to update an existing resource
- `DELETE` to delete an existing resource

For example, to create a new show,
you can use [`curl`](https://curl.se)
to send a `POST` request to the `/shows` endpoint:

```sh
curl \
    --request POST \
    --header "Content-Type: application/json" \
    --data '{"title": "My Show"}' \
    http://localhost:10500/shows
```

And to list all instances for a given week,
you can use `curl` to send a `GET` request to the `/instances` endpoint:

```sh
curl \
    --get \
    --request GET \
    --header "Content-Type: application/json" \
    --data-urlencode "start=2000-01-01T00:00:00Z" \
    --data-urlencode "end=2000-01-08T00:00:00Z" \
    http://localhost:10500/instances
```

## Ping

You can check the status of the service by sending
either a `GET` or `HEAD` request to the `/ping` endpoint.
The service should respond with a `204 No Content` status code.

For example, you can use `curl` to do that:

```sh
curl --request HEAD --head http://localhost:10500/ping
```

## Server-Sent Events

You can subscribe to
[`Server-Sent Events (SSE)`](https://developer.mozilla.org/docs/Web/API/Server-sent_events)
by sending a `GET` request to the `/sse` endpoint.
The service should send you the events as they happen.

For example, you can use `curl` to do that:

```sh
curl --request GET --no-buffer http://localhost:10500/sse
```

## OpenAPI

You can view the [`OpenAPI`](https://www.openapis.org)
documentation made with [`Scalar`](https://scalar.com)
by navigating to the `/openapi` endpoint in your browser.

You can also download the specification in JSON format
by sending a `GET` request to the `/openapi/openapi.json` endpoint.

For example, you can use `curl` to do that:

```sh
curl --request GET http://localhost:10500/openapi/openapi.json
```
