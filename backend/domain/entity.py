from abc import ABC, abstractmethod


class Entity(ABC):
    """Base class for all entities."""

    @abstractmethod
    def id(self) -> str:
        """Return the id of the entity."""
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        """Check if two entities are equal."""
        if not isinstance(other, Entity):
            return False
        return self.id() == other.id()
