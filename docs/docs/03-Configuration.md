---
slug: /configuration
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
- `EMISHOWS__DATABASE__HOST` -
  host of the SQL database of emishows-db
  (default: `localhost`)
- `EMISHOWS__DATABASE__PORT` -
  port of the SQL database of emishows-db
  (default: `34000`)
- `EMISHOWS__DATABASE__PASSWORD` -
  password to authenticate with the SQL database of emishows-db
  (default: `password`)
- `EMISHOWS__EMITIMES__SCHEME` -
  scheme of the CalDAV API of emitimes service
  (default: `http`)
- `EMISHOWS__EMITIMES__HOST` -
  host of the CalDAV API of emitimes service
  (default: `localhost`)
- `EMISHOWS__EMITIMES__PORT` -
  port of the CalDAV API of emitimes service
  (default: `36000`)
- `EMISHOWS__EMITIMES__PATH` -
  path of the CalDAV API of emitimes service
  (default: ``)
- `EMISHOWS__EMITIMES__USER` -
  user to authenticate with the CalDAV API of emitimes service
  (default: `user`)
- `EMISHOWS__EMITIMES__PASSWORD` -
  password to authenticate with the CalDAV API of emitimes service
  (default: `password`)
- `EMISHOWS__EMITIMES__CALENDAR` -
  calendar to use with the CalDAV API of emitimes service
  (default: `emitimes`)
