from domain.project.aggregate import Project
from domain.project.exceptions import RemoteRepositoryDoesNotExistError
from domain.project.factories import ProjectFactory
from domain.project.ports import RemoteRepositoryVerifier


class CreateProjectService:
    """Service for creating a new Project aggregate.

    This service handles the creation of a new Project aggregate with
    all required value objects
    and default policies from the provided policies factory.
    """

    def __init__(
        self,
        project_factory: ProjectFactory,
        remote_repository_verifiers: list[RemoteRepositoryVerifier],
    ):
        """Initialize the service with required dependencies.

        Args:
            project_factory: Factory for creating Project aggregates
            remote_repository_verifiers: List of services for verifying
            remote repository.
        """
        self._project_factory = project_factory
        self._remote_repository_verifiers = remote_repository_verifiers

    async def create(
        self,
        repo_id: str,
        provider: str,
        owner: str,
        rules: list[str],
        url: str,
    ) -> Project:
        """Create a new Project aggregate.

        Args:
            repo_id: ID of the remote repository
            provider: Name of the repository provider (e.g. GitHub)
            owner: Owner of the repository
            rules: List of rules to apply to the project
            url: URL of the repository

        Returns:
            A new Project aggregate

        Raises:
            RemoteRepositoryDoesNotExistError: If the remote repository does not exist
        """
        is_verified = False
        for verifier in self._remote_repository_verifiers:
            is_verified = await verifier.verify(repo_id, provider)
            if is_verified:
                break
        if not is_verified:
            raise RemoteRepositoryDoesNotExistError(repo_id, provider)

        return self._project_factory.create(repo_id, provider, owner, rules, url)
