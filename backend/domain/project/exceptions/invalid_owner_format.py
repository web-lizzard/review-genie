from domain.exception import DomainError


class InvalidOwnerFormatError(DomainError):
    """Error raised when owner has invalid format."""

    def __init__(self) -> None:
        """Initialize invalid owner format error."""
        message = "Invalid owner format"
        super().__init__(message)
