from domain.exception import DomainError


class ProjectAlreadyExistsError(DomainError):
    """Error raised when a project already exists."""

    def __init__(self, project_id: str) -> None:
        """Initialize project already exists error."""
        message = f"Project '{project_id}' already exists'"
        super().__init__(message)
