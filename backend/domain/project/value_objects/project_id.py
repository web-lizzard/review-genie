import re
from dataclasses import dataclass

from ..exceptions import InvalidProjectIdentifierFormatError
from .provider import ProviderType


@dataclass(frozen=True)
class ProjectId:
    """Unique repository identifier in format provider:owner:repo_id."""

    value: str

    def __post_init__(self) -> None:
        parts = self.value.split(":")
        if len(parts) != 3:
            raise InvalidProjectIdentifierFormatError()

        if parts[0] not in ProviderType:
            raise InvalidProjectIdentifierFormatError()

        if not re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$", parts[1]):
            raise InvalidProjectIdentifierFormatError()

        if not re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$", parts[2]):
            raise InvalidProjectIdentifierFormatError()

    @property
    def id(self) -> str:
        return self.value

    def __str__(self) -> str:
        """Return the full identifier string in format provider:owner:repo_id."""
        return self.id
