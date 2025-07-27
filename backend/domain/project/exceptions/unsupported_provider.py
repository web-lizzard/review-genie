from domain.exception import DomainError


class UnsupportedProviderError(DomainError):
    """Error raised when an unsupported provider is used."""

    def __init__(self) -> None:
        """Initialize unsupported provider error."""
        message = "Unsupported provider"
        super().__init__(message)
