from domain.exception import DomainError


class EmptyRepositoryIdError(DomainError):
    """Error raised when repository ID is empty or contains only whitespace."""

    def __init__(self) -> None:
        """Initialize empty repository ID error."""
        message = "Repository ID cannot be empty"
        super().__init__(message)
