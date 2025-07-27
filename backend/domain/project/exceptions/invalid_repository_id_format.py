from domain.exception import DomainError


class InvalidRepositoryIdFormatError(DomainError):
    """Error raised when repository ID has invalid format."""

    def __init__(self) -> None:
        """Initialize invalid repository ID format error."""
        message = "Invalid repository ID format"
        super().__init__(message)
