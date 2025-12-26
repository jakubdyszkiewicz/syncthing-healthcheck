# Syncthing Healthcheck

A lightweight monitoring service for Syncthing devices that sends webhook notifications when devices are healthy and connected.

## Overview

Syncthing Healthcheck periodically checks the status of configured Syncthing devices and sends GET requests to webhook URLs (e.g., [Healthchecks.io](https://healthchecks.io/)) when devices are available and connected within the specified time window.

## Features

- Monitor multiple Syncthing devices
- Configurable check intervals and unavailability thresholds
- Webhook notifications for healthy devices
- Docker support for easy deployment
- Lightweight Python implementation

## Quick Start

### Docker (Recommended)

1. Create a `config.yaml` file (see [Configuration](#configuration))

2. Run the container:

```bash
docker run -d \
  --name syncthing-healthcheck \
  -e SYNCTHING_API_KEY=your-api-key-here \
  -v /path/to/config.yaml:/config/config.yaml \
  jakubdyszkiewicz/syncthing-healthcheck:latest
```

### Docker Compose

```yaml
version: '3'

services:
  syncthing-healthcheck:
    image: jakubdyszkiewicz/syncthing-healthcheck:latest
    environment:
      - SYNCTHING_API_KEY=your-api-key-here
    volumes:
      - ./config.yaml:/config/config.yaml
    restart: unless-stopped
```

### Local Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set the API key environment variable:

```bash
export SYNCTHING_API_KEY=your-api-key-here
```

3. Run the healthcheck:

```bash
python healthcheck.py
```

## Configuration

Create a `config.yaml` file with the following structure:

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

### Configuration Options

- `check_interval`: How often to check device status (e.g., `1h`, `30m`, `3600s`)
- `syncthing.url`: URL of your Syncthing instance
- `devices`: List of devices to monitor
  - `id`: Syncthing device ID
  - `max_unavailability`: Maximum time a device can be unavailable before considered unhealthy (e.g., `168h` = 7 days)
  - `webhook_url`: URL to call when device is healthy

### Environment Variables

- `SYNCTHING_API_KEY` (required): Your Syncthing API key
- `CONFIG_PATH` (optional): Path to config file (default: `/config/config.yaml`)

## How It Works

1. The service periodically queries the Syncthing API endpoint `/rest/stats/device`
2. For each configured device, it checks the `lastSeen` timestamp
3. If a device was seen within its `max_unavailability` window, a GET request is sent to its webhook URL
4. The process repeats according to the `check_interval`

## Finding Your Syncthing API Key

1. Open Syncthing web UI
2. Go to Actions > Advanced > GUI
3. Copy the API Key from the settings page

## Finding Device IDs

1. Open Syncthing web UI
2. Pick a device and click "see QR code"

## Integration with Healthchecks.io

This service works great with [Healthchecks.io](https://healthchecks.io/) for monitoring:

1. Create a check on Healthchecks.io for each device
2. Set the period to match your `check_interval`3. Set the grace time to slightly more than `check_interval`
4. Use the ping URL as the `webhook_url` in your config

## Development

### Running Locally

```bash
python3 -m venv venv/
source venv/bin/activate.fish
pip install -r requirements.txt

# Set environment variables
export SYNCTHING_API_KEY=your-api-key
export CONFIG_PATH=config.yaml

# Run the application
python healthcheck.py
```

### Building Docker Image

```bash
docker build -t syncthing-healthcheck .
```