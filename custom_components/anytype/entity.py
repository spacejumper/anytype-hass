"""Base entities for the Anytype integration."""

from typing import Any

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import AnyTypeCoordinator


class AnyTypeEntity(CoordinatorEntity[AnyTypeCoordinator]):
    """Base entity backed by Anytype coordinator data."""

    def __init__(
        self,
        coordinator: AnyTypeCoordinator,
        space_id: str,
        object_id: str | None = None,
    ) -> None:
        """Initialize the Anytype coordinator entity."""
        super().__init__(coordinator, context=space_id)
        self.space_id = space_id
        self.object_id = object_id

    @property
    def space_data(self) -> dict[str, Any]:
        """Return the coordinator data for the current space."""
        return self.coordinator.data.get(self.space_id, {})

    @property
    def space(self) -> dict[str, Any]:
        """Return details for the current space."""
        space = self.space_data.get("space")
        if isinstance(space, dict):
            return space
        return {}

    @property
    def tasks(self) -> list[dict[str, Any]]:
        """Return tasks for the current space."""
        tasks = self.space_data.get("tasks")
        if isinstance(tasks, list):
            return [task for task in tasks if isinstance(task, dict)]
        return []

    @property
    def objects(self) -> list[dict[str, Any]]:
        """Return objects for the current space."""
        objects = self.space_data.get("objects")
        if isinstance(objects, list):
            return [obj for obj in objects if isinstance(obj, dict)]
        return []

    @property
    def object_data(self) -> dict[str, Any]:
        """Return details for the configured object ID."""
        if self.object_id is None:
            return {}

        for obj in self.objects:
            if obj.get("id") == self.object_id:
                return obj

        return {}
