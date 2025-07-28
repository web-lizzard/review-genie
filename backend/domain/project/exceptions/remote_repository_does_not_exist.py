from domain.exception import DomainError


class RemoteRepositoryDoesNotExistError(DomainError):
    """Error raised when a remote repository does not exist."""

    def __init__(self, repository_id: str, provider: str) -> None:
        """Initialize remote repository does not exist error."""
        message = (
            f"Remote repository '{repository_id}' "
            f"does not exist on provider '{provider}'"
        )
        super().__init__(message)
