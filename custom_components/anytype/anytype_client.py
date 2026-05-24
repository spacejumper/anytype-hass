"""Async client for Anytype."""

import asyncio
from typing import Any

import aiohttp

from homeassistant.exceptions import HomeAssistantError

API_VERSION = "2025-11-08"


class AnytypeError(HomeAssistantError):
    """Base Anytype exception."""


class CannotConnect(AnytypeError):
    """Cannot connect to API."""


class InvalidAuth(AnytypeError):
    """Invalid authentication."""


class AnytypeClient:
    """Async Anytype API client."""

    def __init__(
        self,
        host: str,
        port: int,
        api_key: str,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """Initialize client."""
        self._base_url = f"http://{host}:{port}"
        self._api_key = api_key
        self._session = session

    # Session handling
    def _get_session(self) -> aiohttp.ClientSession:
        """Return active session or raise if missing."""
        if self._session is None:
            raise RuntimeError(
                "AnytypeClient session not set. Use async_get_clientsession(hass)."
            )
        return self._session

    # Headers
    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Anytype-Version": API_VERSION,
            "Authorization": f"Bearer {self._api_key}",
        }

    # Core request
    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make request."""
        url = f"{self._base_url}{endpoint}"
        session = self._get_session()

        try:
            async with asyncio.timeout(10):
                async with session.request(
                    method,
                    url,
                    headers=self._headers,
                    json=json_data,
                ) as resp:
                    resp_json = await resp.json()
                    if resp.status in (401, 403):
                        raise InvalidAuth(
                            f"{resp.status}: {resp_json.get('message', 'Unauthorized')}"
                        )

                    if resp.status == 429:
                        raise AnytypeError("Rate limit exceeded")

                    if 400 <= resp.status < 500:
                        raise AnytypeError(
                            f"Client error {resp.status}: {resp_json.get('message', 'Bad Request')}"
                        )

                    if resp.status >= 500:
                        raise CannotConnect(
                            f"Server error {resp.status}: {resp_json.get('message', 'Server Error')}"
                        )

                    return await resp.json()

        except TimeoutError as err:
            raise CannotConnect("Request timed out") from err
        except aiohttp.ClientError as err:
            raise CannotConnect("Failed to connect to Anytype API") from err

    # API interactions
    async def async_get_spaces(self) -> list[dict[str, Any]]:
        """Get spaces."""
        data = await self._request("GET", "/v1/spaces")
        spaces = data.get("data", [])

        def is_space(item: dict[str, Any]) -> bool:
            return (
                item.get("type") == "anytype.space"
                or item.get("object") == "anytype.space"
            )

        return [space for space in spaces if is_space(space)]

    async def async_get_tasks(self, space_id: str) -> list[dict[str, Any]]:
        """Get tasks."""
        data = await self._request(
            "POST",
            f"/v1/spaces/{space_id}/search",
            json_data={
                "filters": {
                    "conditions": [
                        {
                            "checkbox": False,
                            "condition": "eq",
                            "property_key": "done",
                        }
                    ]
                },
                "sort": {"direction": "desc", "property_key": "last_modified_date"},
                "types": ["task"],
            },
        )

        return data.get("data", [])

    # fetch object in detail
    async def async_get_space_object_detail(
        self, space_id: str, object_id: str
    ) -> dict[str, Any]:
        """Get details of a specific object in a space."""
        data = await self._request(
            "GET",
            f"/v1/spaces/{space_id}/objects/{object_id}",
        )
        return data.get("object", {})

    # fetch objects in detail (first get all, then filter, then fetch details concurrently)
    async def async_get_space_objects(self, space_id: str) -> list[dict[str, Any]]:
        """Get filtered objects in a space, then enrich with details."""

        data = await self._request(
            "GET",
            f"/v1/spaces/{space_id}/objects",
        )

        objects = data.get("data", [])

        TARGET_KEY = "tag"
        TARGET_NAME = "hass"

        filtered_ids = {
            obj_id
            for obj in objects
            if (obj_id := obj.get("id"))
            and any(
                prop.get("key") == TARGET_KEY
                and any(
                    tag.get("name") == TARGET_NAME
                    for tag in prop.get("multi_select", [])
                )
                for prop in obj.get("properties", [])
            )
        }

        return await asyncio.gather(
            *(
                self.async_get_space_object_detail(space_id, object_id)
                for object_id in filtered_ids
            )
        )

    # validate connection (for config flow)
    async def async_validate_connection(self) -> bool:
        """Validate API."""
        await self.async_get_spaces()
        return True

    async def async_get_network_ids(self) -> list[str]:
        """Get network IDs for all spaces."""
        spaces = await self.async_get_spaces()
        if not spaces:
            raise CannotConnect("No spaces found - check connection and API key")

        return [
            network_id for space in spaces if (network_id := space.get("network_id"))
        ]
