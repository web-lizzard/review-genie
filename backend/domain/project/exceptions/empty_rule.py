from domain.exception import DomainError


class EmptyRuleError(DomainError):
    """Error raised when trying to add an empty rule."""

    def __init__(self) -> None:
        """Initialize empty rule error."""
        message = "Rule cannot be empty"
        super().__init__(message)
