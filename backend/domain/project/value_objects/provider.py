from dataclasses import dataclass
from enum import Enum

from ..exceptions import UnsupportedProviderError


class ProviderType(str, Enum):
    """Supported repository providers."""

    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"


@dataclass(frozen=True)
class Provider:
    """Repository service provider value object."""

    value: ProviderType

    def __post_init__(self) -> None:
        """Validate the provider value."""
        if self.value not in ProviderType:
            raise UnsupportedProviderError()

    def __str__(self) -> str:
        return str(self.value.value)
