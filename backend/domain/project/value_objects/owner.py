import re
from dataclasses import dataclass

from ..exceptions import InvalidOwnerFormatError


@dataclass(frozen=True)
class Owner:
    """Repository owner identifier with validation."""

    value: str

    def __post_init__(self) -> None:
        """Validate owner value."""
        self._validate()

    def _validate(self) -> None:
        """Validate that owner is not empty and contains valid characters."""
        if not self.value or not self.value.strip():
            raise InvalidOwnerFormatError()

        stripped_value = self.value.strip()
        if not re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$", stripped_value):
            raise InvalidOwnerFormatError()

        object.__setattr__(self, "value", stripped_value)

    def __str__(self) -> str:
        """Return the owner value."""
        return self.value
