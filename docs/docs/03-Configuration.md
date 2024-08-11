---
slug: /config
title: Configuration
---

## Environment variables

You can configure the app at runtime using various environment variables:

- `EMISHOWS__SERVER__HOST` -
  host to run the server on
  (default: `0.0.0.0`)
- `EMISHOWS__SERVER__PORT` -
  port to run the server on
  (default: `35000`)
- `EMISHOWS__SERVER__TRUSTED` -
  trusted IP addresses
  (default: `*`)
- `EMISHOWS__DATASHOWS__SQL__HOST` -
  host of the SQL database of datashows
  (default: `localhost`)
- `EMISHOWS__DATASHOWS__SQL__PORT` -
  port of the SQL database of datashows
  (default: `34000`)
- `EMISHOWS__DATASHOWS__SQL__PASSWORD` -
  password to authenticate with the SQL database of datashows
  (default: `password`)
- `EMISHOWS__DATATIMES__CALDAV__SCHEME` -
  scheme of the CalDAV API of datatimes service
  (default: `http`)
- `EMISHOWS__DATATIMES__CALDAV__HOST` -
  host of the CalDAV API of datatimes service
  (default: `localhost`)
- `EMISHOWS__DATATIMES__CALDAV__PORT` -
  port of the CalDAV API of datatimes service
  (default: `36000`)
- `EMISHOWS__DATATIMES__CALDAV__PATH` -
  path of the CalDAV API of datatimes service
  (default: ``)
- `EMISHOWS__DATATIMES__CALDAV__USER` -
  user to authenticate with the CalDAV API of datatimes service
  (default: `user`)
- `EMISHOWS__DATATIMES__CALDAV__PASSWORD` -
  password to authenticate with the CalDAV API of datatimes service
  (default: `password`)
- `EMISHOWS__DATATIMES__CALDAV__CALENDAR` -
  calendar to use with the CalDAV API of datatimes service
  (default: `datatimes`)
- `EMISHOWS__DEBUG` -
  enable debug mode
  (default: `false`)
