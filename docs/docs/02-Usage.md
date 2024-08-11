---
slug: /usage
title: Usage
---

## Managing shows and events

You can manage shows and events using
the `/shows` and `/events` endpoints.
The API follows RESTful conventions,
so you can use the following HTTP methods:

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
    http://localhost:35000/shows
```

## Retrieving the schedule

Events themselves only contain the information
about start and end times of the first instance
and the recurrence rule.
To make it easier to retrieve event instances
for a given time range,
there is a `/schedule` endpoint.
It expands the recurrence rule
into event instances in the given time range.

For example, to retrieve the schedule for a given week,
you can use [`curl`](https://curl.se)
to send a `GET` request to the `/schedule` endpoint:

```sh
curl \
    --get \
    --request GET \
    --header "Content-Type: application/json" \
    --data-urlencode "start=2024-01-01T00:00:00" \
    --data-urlencode "end=2024-01-08T00:00:00" \
    http://localhost:35000/schedule
```

The start and end times should be in the UTC timezone.

## Ping

You can check the status of the app by sending
either a `GET` or `HEAD` request to the `/ping` endpoint.
The app should respond with a `204 No Content` status code.

For example, you can use `curl` to do that:

```sh
curl \
    --request HEAD \
    --head \
    http://localhost:35000/ping
```

## Server-Sent Events

You can subscribe to the Server-Sent Events (SSE) by sending
a `GET` request to the `/sse` endpoint.
The app will send you the events as they happen.

For example, you can use `curl` to do that:

```sh
curl \
    --request GET \
    --no-buffer \
    http://localhost:35000/sse
```
