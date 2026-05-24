"""Shared data coordinator for the Anytype integration."""

import asyncio
from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .anytype_client import AnytypeClient, AnytypeError, CannotConnect, InvalidAuth
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class AnyTypeCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Coordinate Anytype API polling."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        client: AnytypeClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=timedelta(seconds=30),
            always_update=False,
        )
        self.client = client

    async def _async_fetch_space_data(
        self,
        space: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        """Fetch all data for a single space."""
        space_id = space["id"]
        return space_id, {
            "space": space,
            "tasks": await self.client.async_get_tasks(space_id),
            "objects": await self.client.async_get_space_objects(space_id),
        }

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch the latest Anytype data."""
        try:
            async with asyncio.timeout(10):
                spaces = await self.client.async_get_spaces()

                listening_space_ids = set(self.async_contexts())
                if listening_space_ids:
                    spaces = [
                        space for space in spaces if space["id"] in listening_space_ids
                    ]

                results = await asyncio.gather(
                    *(self._async_fetch_space_data(space) for space in spaces)
                )
                return dict(results)
        except InvalidAuth as err:
            raise ConfigEntryAuthFailed from err
        except CannotConnect as err:
            raise UpdateFailed(f"Failed communicating with Anytype: {err}") from err
        except AnytypeError as err:
            if "Rate limit exceeded" in str(err):
                raise UpdateFailed(retry_after=60) from err
            raise UpdateFailed(f"Error communicating with Anytype: {err}") from err
        except TimeoutError as err:
            raise UpdateFailed("Timeout communicating with Anytype") from err
