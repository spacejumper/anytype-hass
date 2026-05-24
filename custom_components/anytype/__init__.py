"""The AnyType integration."""

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .anytype_client import AnytypeClient, CannotConnect, InvalidAuth
from .coordinator import AnyTypeCoordinator

_PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.TODO]


@dataclass(slots=True)
class AnytypeRuntimeData:
    """Runtime data for the AnyType integration."""

    client: AnytypeClient
    coordinator: AnyTypeCoordinator


type AnytypeConfigEntry = ConfigEntry[AnytypeRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: AnytypeConfigEntry) -> bool:
    """Set up AnyType from a config entry."""

    session = async_get_clientsession(hass)

    client = AnytypeClient(
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
        entry.data[CONF_API_KEY],
        session=session,
    )

    try:
        await client.async_validate_connection()
    except CannotConnect as err:
        raise ConfigEntryNotReady from err
    except InvalidAuth as err:
        raise ConfigEntryAuthFailed from err

    coordinator = AnyTypeCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = AnytypeRuntimeData(client=client, coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: AnytypeConfigEntry,
) -> bool:
    """Unload a config entry."""

    return await hass.config_entries.async_unload_platforms(
        entry,
        _PLATFORMS,
    )
