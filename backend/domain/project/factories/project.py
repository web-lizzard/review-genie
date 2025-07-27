from datetime import datetime

from domain.project import factories
from domain.project import value_objects as vo
from domain.project.aggregate import Project


class ProjectFactory:
    """Factory for creating Project aggregates.

    This factory handles the creation of Project aggregates with
    all required value objects and default policies from the provided policies factory.
    """

    def __init__(self, policies_factory: factories.PoliciesFactory):
        """Initialize the ProjectFactory.

        Args:
            policies_factory: Factory for creating default project policies
        """
        self._policies_factory = policies_factory

    def create(
        self,
        repo_id: str,
        provider: str,
        owner: str,
        rules: list[str],
        url: str,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> Project:
        """Create a new Project aggregate.

        Args:
            repo_id: External repository identifier
            provider: Repository provider (e.g. 'github', 'gitlab')
            owner: Repository owner
            rules: List of code review rules
            url: Repository URL
            created_at: Optional creation timestamp
            updated_at: Optional last update timestamp

        Returns:
            A new Project aggregate instance
        """
        project_id = vo.ProjectId(f"{provider}:{owner}:{repo_id}")
        provider_type = vo.ProviderType(provider)
        policies = self._policies_factory.create_policies()

        return Project(
            project_id=project_id,
            repo_id=vo.RepositoryId(repo_id),
            provider=vo.Provider(provider_type),
            policies=policies,
            rules=vo.Rules(rules),
            url=url,
            owner=vo.Owner(owner),
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now(),
        )
