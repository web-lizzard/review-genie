from domain.project import value_objects as vo
from domain.project.aggregate import Project
from domain.project.exceptions import RemoteRepositoryDoesNotExistError
from domain.project.factories import ProjectFactory, ValueObjectsFactory
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
        value_objects_factory: ValueObjectsFactory,
        remote_repository_verifiers: list[RemoteRepositoryVerifier],
    ):
        """Initialize the service with required dependencies.

        Args:
            project_factory: Factory for creating Project aggregates
            value_objects_factory: Factory for creating project value objects from URL
            remote_repository_verifiers: List of services for verifying
            remote repository.
        """
        self._project_factory = project_factory
        self._value_objects_factory = value_objects_factory
        self._remote_repository_verifiers = remote_repository_verifiers

    async def create(
        self,
        url: str,
        rules: list[str],
    ) -> Project:
        """Create a new Project aggregate.

        Args:
            url: URL of the repository
            rules: List of rules to apply to the project

        Returns:
            A new Project aggregate

        Raises:
            RemoteRepositoryDoesNotExistError: If the remote repository does not exist
            InvalidUrlFormatError: If URL format is invalid
            UnsupportedProviderError: If provider is not supported
        """
        url_vo = vo.URL(url)
        project_value_objects = self._value_objects_factory.create_from_url(url_vo)

        repo_id = project_value_objects.repository_id
        provider = project_value_objects.provider

        is_verified = False
        for verifier in self._remote_repository_verifiers:
            is_verified = await verifier.verify(
                repository_id=repo_id, provider=provider
            )
            if is_verified:
                break
        if not is_verified:
            raise RemoteRepositoryDoesNotExistError(repo_id, provider)

        return self._project_factory.create(url, rules)
