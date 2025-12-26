# Instruction

## Overview

I need to monitor devices connected to [Syncthing](https://syncthing.net/).

Write a python software that has such config

```yaml
check_interval: 1h
syncthing:
  url: http://syncthing:8384
devices:
  - id: XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX
    max_unavailability: 168h
    webhook_url: "https://hc-ping.com/00000000-0000-0000-0000-000000000000"
  - id: XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX-XXXXXXX-YYYYYYY
    max_unavailability: 168h
    webhook_url: "https://hc-ping.com/00000000-0000-0000-0000-000000000001"
```

Additionally, `SYNCTHING_API_KEY` is required and it's added to all requests to Syncthing.

It runs a process every "check_interval".
On every process run it uses this API
```
GET http://localhost:8384/rest/stats/device
```
wit such response
```json
{
  "P56IOI7-MZJNU2Y-IQGDREY-DM2MGTI-MGL3BXN-PQ6W5BM-TBBZ4TJ-XZWICQ2": {
    "lastSeen" : "2015-04-18T11:21:31.3256277+01:00"
    "lastConnectionDurationS": 556335.421708141
  }
}
```
to check the state of the device.
If device is seen no later than max_unavailability, send a GET request to webhook url.

## Distribution

Docker file with Github Action to build and publish docker container on pushed tag.
Docker repo: jakubdyszkiewicz/syncthing-healthcheck

## License

Apache 2.0

## Other

Gitignore for vscode, sample config and intellij idea.
Write README.md