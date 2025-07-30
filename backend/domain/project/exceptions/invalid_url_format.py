from domain.exception import DomainError


class InvalidUrlFormatError(DomainError):
    """Error raised when URL has invalid format."""

    def __init__(self) -> None:
        """Initialize invalid URL format error."""
        message = (
            "Invalid URL format. URL must be a valid GitHub, GitLab, or "
            + "Bitbucket repository URL with username and project name"
        )
        super().__init__(message)
