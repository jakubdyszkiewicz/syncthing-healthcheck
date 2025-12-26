#!/usr/bin/env python3

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yaml
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Config:
    """Configuration model for the healthcheck"""

    def __init__(self, config_dict: dict):
        self.check_interval = self._parse_duration(config_dict.get('check_interval', '1h'))
        syncthing_config = config_dict.get('syncthing', {})
        self.syncthing_url = syncthing_config.get('url', 'http://localhost:8384')
        self.devices = config_dict.get('devices', [])

    @staticmethod
    def _parse_duration(duration_str: str) -> int:
        """Parse duration string (e.g., '1h', '168h', '30m') to seconds"""
        duration_str = duration_str.strip()
        if duration_str.endswith('h'):
            return int(duration_str[:-1]) * 3600
        elif duration_str.endswith('m'):
            return int(duration_str[:-1]) * 60
        elif duration_str.endswith('s'):
            return int(duration_str[:-1])
        else:
            raise ValueError(f"Invalid duration format: {duration_str}")

    @classmethod
    def from_file(cls, config_path: str) -> 'Config':
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        return cls(config_dict)


class SyncthingHealthcheck:
    """Main healthcheck service"""

    def __init__(self, config: Config, api_key: str):
        self.config = config
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({'X-API-Key': api_key})

    def get_device_stats(self) -> Dict:
        """Fetch device statistics from Syncthing API"""
        url = f"{self.config.syncthing_url}/rest/stats/device"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch device stats: {e}")
            return {}

    def check_device(self, device_config: dict, device_stats: Dict) -> bool:
        """Check if a device is healthy and send webhook if needed"""
        device_id = device_config['id']
        max_unavailability = Config._parse_duration(device_config['max_unavailability'])
        webhook_url = device_config['webhook_url']

        device_stat = device_stats.get(device_id)
        if not device_stat:
            logger.warning(f"Device {device_id} not found in stats")
            return False

        last_seen_str = device_stat.get('lastSeen')
        if not last_seen_str:
            logger.warning(f"Device {device_id} has no lastSeen timestamp")
            return False

        try:
            # Parse ISO 8601 timestamp
            last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
            now = datetime.now(last_seen.tzinfo)

            time_since_seen = (now - last_seen).total_seconds()

            if time_since_seen <= max_unavailability:
                logger.info(f"Device {device_id} is healthy (last seen {time_since_seen:.0f}s ago)")
                self.send_webhook(webhook_url, device_id)
                return True
            else:
                logger.warning(f"Device {device_id} is unavailable (last seen {time_since_seen:.0f}s ago, max: {max_unavailability}s)")
                return False
        except Exception as e:
            logger.error(f"Error checking device {device_id}: {e}")
            return False

    def send_webhook(self, webhook_url: str, device_id: str):
        """Send GET request to webhook URL"""
        try:
            response = requests.get(webhook_url, timeout=10)
            response.raise_for_status()
            logger.info(f"Webhook sent successfully for device {device_id}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send webhook for device {device_id}: {e}")

    def check_all_devices(self):
        """Check all configured devices"""
        logger.info("Starting device health check")
        device_stats = self.get_device_stats()

        if not device_stats:
            logger.error("No device stats available, skipping check")
            return

        for device_config in self.config.devices:
            self.check_device(device_config, device_stats)

        logger.info("Device health check completed")

    def run(self):
        """Run the healthcheck service continuously"""
        logger.info(f"Starting Syncthing Healthcheck (interval: {self.config.check_interval}s)")

        while True:
            try:
                self.check_all_devices()
            except Exception as e:
                logger.error(f"Error during health check: {e}", exc_info=True)

            logger.info(f"Sleeping for {self.config.check_interval}s")
            time.sleep(self.config.check_interval)


def main():
    """Main entry point"""
    config_path = os.environ.get('CONFIG_PATH', '/config/config.yaml')
    api_key = os.environ.get('SYNCTHING_API_KEY')

    if not api_key:
        logger.error("SYNCTHING_API_KEY environment variable is required")
        sys.exit(1)

    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        sys.exit(1)

    try:
        config = Config.from_file(config_path)
        healthcheck = SyncthingHealthcheck(config, api_key)
        healthcheck.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
