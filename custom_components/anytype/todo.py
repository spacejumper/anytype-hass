"""Todo support for Anytype."""

from homeassistant.components.todo import TodoItem, TodoItemStatus, TodoListEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import AnytypeConfigEntry
from .entity import AnyTypeEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AnytypeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Anytype object todos."""

    coordinator = entry.runtime_data.coordinator

    entities = [
        AnytypeObjectTodo(
            coordinator=coordinator,
            space_id=space_id,
        )
        for space_id in coordinator.data
    ]

    async_add_entities(entities)


class AnytypeObjectTodo(AnyTypeEntity, TodoListEntity):
    """Todo per Anytype object."""

    def __init__(self, coordinator, space_id: str) -> None:
        """Initialize the Anytype todo entity."""
        super().__init__(coordinator, space_id=space_id)
        self._attr_has_entity_name = True
        self._attr_unique_id = f"anytype_todo_{space_id}"

    @property
    def name(self) -> str:
        """Return the entity name."""
        return f"Anytype {self.space.get('name', 'Unnamed')}"

    @property
    def todo_items(self) -> list[TodoItem]:
        """Return a list of TodoItem for the current tasks.

        Each task is converted into a TodoItem with a unique uid, summary and
        default status of NEEDS_ACTION.
        """
        tasks = self.tasks
        return [
            TodoItem(
                uid=str(i),
                summary=task.get("name", "Unnamed Task"),
                status=TodoItemStatus.NEEDS_ACTION,
            )
            for i, task in enumerate(tasks)
        ]
