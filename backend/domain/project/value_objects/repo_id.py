import re
from dataclasses import dataclass

from ..exceptions import EmptyRepositoryIdError, InvalidRepositoryIdFormatError


@dataclass(frozen=True)
class RepositoryId:
    """Repository identifier with validation."""

    value: str

    def __post_init__(self) -> None:
        """Validate repo_id value."""
        self._validate()

    def _validate(self) -> None:
        """Validate that repo_id is not empty and contains valid characters."""
        if not self.value or not self.value.strip():
            raise EmptyRepositoryIdError()

        # Basic validation for repository name format
        stripped_value = self.value.strip()
        if not re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$", stripped_value):
            raise InvalidRepositoryIdFormatError()

        # Update the stripped value
        object.__setattr__(self, "value", stripped_value)

    def __str__(self) -> str:
        """Return the repository ID value."""
        return self.value
