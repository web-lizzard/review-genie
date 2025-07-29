import re


class DomainError(Exception):
    """Base class for domain exceptions."""

    def __init__(self, message: str):
        """Initialize domain error.

        Args:
            message: Error message
        """
        super().__init__(message)
        self.message = message
        self.status = self._derive_status_from_class_name()

    def _derive_status_from_class_name(self) -> str:
        """Derive status from class name.

        Converts class name from CamelCase to snake_case, removing 'Error' suffix.

        Returns:
            Status string
        """
        class_name = self.__class__.__name__
        if class_name.endswith("Error"):
            class_name = class_name[:-5]  # Remove "Error" suffix

        # Convert CamelCase to snake_case
        return re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).lower()


class EntityNotFoundError(DomainError):
    def __init__(self) -> None:
        """Initialize entity not found error.

        Args:
            entity_type: Type of entity
            entity_id: ID of entity
        """
        super().__init__("Entity not found")
