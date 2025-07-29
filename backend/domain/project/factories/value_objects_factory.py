from abc import ABC, abstractmethod
from dataclasses import dataclass

from domain.project import value_objects as vo


@dataclass(frozen=True)
class ProjectValueObjects:
    """Container for project value objects created by the factory."""

    project_id: vo.ProjectId
    repository_id: vo.RepositoryId
    provider: vo.Provider
    owner: vo.Owner


class ValueObjectsFactory(ABC):
    """Abstract factory for creating project value objects."""

    @abstractmethod
    def create_from_url(self, url: vo.URL) -> ProjectValueObjects:
        """Create project value objects from a URL.

        Args:
            url: Repository URL value object

        Returns:
            ProjectValueObjects containing all the created value objects
        """
        pass


class URLBasedValueObjectsFactory(ValueObjectsFactory):
    """Concrete factory that creates value objects by extracting data from URL."""

    def create_from_url(self, url: vo.URL) -> ProjectValueObjects:
        """Create project value objects from a URL.

        Args:
            url: Repository URL value object

        Returns:
            ProjectValueObjects containing all the created value objects

        Raises:
            InvalidUrlFormatError: If URL format is invalid
            UnsupportedProviderError: If provider is not supported
        """
        # Extract provider from URL
        provider_str = url.get_provider()
        provider_type = vo.ProviderType(provider_str)
        provider = vo.Provider(provider_type)

        # Extract owner and repository name from URL
        owner_str, repo_name = url.get_username_and_project()
        owner = vo.Owner(owner_str)
        repository_id = vo.RepositoryId(repo_name)

        # Create project ID in format: provider:owner:repo_id
        project_id_str = f"{provider_str}:{owner_str}:{repo_name}"
        project_id = vo.ProjectId(project_id_str)

        return ProjectValueObjects(
            project_id=project_id,
            repository_id=repository_id,
            provider=provider,
            owner=owner,
        )
