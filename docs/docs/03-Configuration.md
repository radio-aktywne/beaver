---
slug: /config
title: Configuration
---

## Environment variables

You can configure the service at runtime using various environment variables:

- `BEAVER__SERVER__HOST` -
  host to run the server on
  (default: `0.0.0.0`)
- `BEAVER__SERVER__PORT` -
  port to run the server on
  (default: `10500`)
- `BEAVER__SERVER__TRUSTED` -
  trusted IP addresses
  (default: `*`)
- `BEAVER__HOWLITE__CALDAV__SCHEME` -
  scheme of the CalDAV API of howlite database
  (default: `http`)
- `BEAVER__HOWLITE__CALDAV__HOST` -
  host of the CalDAV API of howlite database
  (default: `localhost`)
- `BEAVER__HOWLITE__CALDAV__PORT` -
  port of the CalDAV API of howlite database
  (default: `10520`)
- `BEAVER__HOWLITE__CALDAV__PATH` -
  path of the CalDAV API of howlite database
  (default: ``)
- `BEAVER__HOWLITE__CALDAV__USER` -
  user to authenticate with the CalDAV API of howlite database
  (default: `user`)
- `BEAVER__HOWLITE__CALDAV__PASSWORD` -
  password to authenticate with the CalDAV API of howlite database
  (default: `password`)
- `BEAVER__HOWLITE__CALDAV__CALENDAR` -
  calendar to use with the CalDAV API of howlite database
  (default: `calendar`)
- `BEAVER__SAPPHIRE__SQL__HOST` -
  host of the SQL database of sapphire
  (default: `localhost`)
- `BEAVER__SAPPHIRE__SQL__PORT` -
  port of the SQL database of sapphire
  (default: `10510`)
- `BEAVER__SAPPHIRE__SQL__PASSWORD` -
  password to authenticate with the SQL database of sapphire
  (default: `password`)
- `BEAVER__DEBUG` -
  enable debug mode
  (default: `true`)
