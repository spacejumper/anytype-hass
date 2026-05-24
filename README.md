# AnyType Home Assistant Integration

Custom integration to connect Home Assistant to an AnyType server.

## Features
- Connect to a self-hosted AnyType API
- Configure via the UI (config flow)
- Provides sensors for AnyType status

## Installation

### HACS
1. Add this repository as a custom repository in HACS (Integration category).
2. Install the "AnyType" integration.
3. Restart Home Assistant.
4. Go to Settings > Devices & Services and add "AnyType".

### Manual
1. Copy `custom_components/anytype` into your Home Assistant config `custom_components` directory.
2. Restart Home Assistant.
3. Go to Settings > Devices & Services and add "AnyType".

## Configuration
You will need:
- Hostname or IP of the AnyType server
- Port (default: 31012)
- API key

These are entered during the config flow.

## Troubleshooting
- Verify the AnyType API is reachable from Home Assistant.
- Check Home Assistant logs for connection errors.

## Support
Create an issue in this repository with logs and reproduction steps.
