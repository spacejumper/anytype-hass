# AnyType Home Assistant Integration

Connect Home Assistant to AnyType and surface your workspace inside HA. ✨

## What this add-on does
- Shows AnyType data as Home Assistant entities 📌
- All tasks are exposed as todos (so you can see and manage them in HA) ✅
- All pages tagged with `hass` are exposed for quick access 🏷️
- Connects to a self-hosted AnyType CLI (API) 🔌
- Configures via the UI (config flow) ⚙️

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

## Data shown in Home Assistant
- Todos: all AnyType tasks are listed as HA todos
- Pages: any AnyType page tagged with `hass` is listed

## Troubleshooting
- Verify the AnyType API is reachable from Home Assistant.
- Check Home Assistant logs for connection errors.

## Support
Create an issue in this repository with logs and reproduction steps.

## Roadmap / Todo
- Use the filter API to query only `hass`-tagged pages
- Add the ability to check off a todo/task from Home Assistant
