from domain.exception import DomainError


class InvalidProjectIdentifierFormatError(DomainError):
    """Error raised when project identifier has invalid format."""

    def __init__(self) -> None:
        """Initialize invalid project identifier format error."""
        message = "Invalid project identifier format"
        super().__init__(message)
