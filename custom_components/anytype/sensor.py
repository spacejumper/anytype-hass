"""Sensor support for Anytype."""

from collections.abc import Mapping
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import AnytypeConfigEntry
from .entity import AnyTypeEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AnytypeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Anytype object sensors."""

    coordinator = entry.runtime_data.coordinator

    entities: list[AnytypeSensor] = []

    for space_id, data in coordinator.data.items():
        objects = data.get("objects", [])
        if not isinstance(objects, list):
            continue
        entities.extend(
            AnytypeSensor(
                coordinator=coordinator,
                space_id=space_id,
                object_id=obj["id"],
            )
            for obj in objects
            if isinstance(obj, dict) and "id" in obj
        )

    async_add_entities(entities)


class AnytypeSensor(AnyTypeEntity, SensorEntity):
    """Sensor per Anytype object."""

    def __init__(
        self,
        coordinator,
        space_id: str,
        object_id: str,
    ) -> None:
        """Initialize the Anytype sensor."""
        super().__init__(coordinator, space_id=space_id, object_id=object_id)
        self._attr_has_entity_name = True
        self._attr_unique_id = f"anytype_obj_{object_id}"

    @property
    def name(self) -> str:
        """Return the sensor name."""
        return f"Anytype {self.object_data.get('name', 'Unnamed')}"

    @property
    def native_value(self) -> str | None:
        """Main value = last_modified_date."""
        obj = self.object_data
        if not obj:
            return None

        properties = obj.get("properties", [])
        if not isinstance(properties, list):
            return None

        return next(
            (
                prop.get("date")
                for prop in properties
                if isinstance(prop, dict) and prop.get("key") == "last_modified_date"
            ),
            None,
        )

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return the state attributes."""
        obj = self.object_data
        if not obj:
            return {"markdown": "Missing"}

        name = obj.get("name", "Unnamed")
        markdown = obj.get("markdown", "")
        icon = (obj.get("icon") or {}).get("emoji", "")

        lines: list[str] = []
        lines.append(f"# {icon} {name}".strip())

        if markdown:
            lines.append(f"> {markdown}")

        return {
            "markdown": "\n".join(lines).strip(),
        }
