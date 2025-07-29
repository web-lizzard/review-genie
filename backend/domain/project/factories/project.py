from datetime import datetime

from domain.project import factories
from domain.project import value_objects as vo
from domain.project.aggregate import Project


class ProjectFactory:
    """Factory for creating Project aggregates.

    This factory handles the creation of Project aggregates with
    all required value objects and default policies from the provided policies factory.
    """

    def __init__(
        self,
        policies_factory: factories.PoliciesFactory,
        value_objects_factory: factories.ValueObjectsFactory,
    ):
        """Initialize the ProjectFactory.

        Args:
            policies_factory: Factory for creating default project policies
            value_objects_factory: Factory for creating project value objects from URL
        """
        self._policies_factory = policies_factory
        self._value_objects_factory = value_objects_factory

    def create(
        self,
        url: str,
        rules: list[str],
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> Project:
        """Create a new Project aggregate.

        Args:
            url: Repository URL string
            rules: List of code review rules
            created_at: Optional creation timestamp
            updated_at: Optional last update timestamp

        Returns:
            A new Project aggregate instance
        """
        url_vo = vo.URL(url)
        project_value_objects = self._value_objects_factory.create_from_url(url_vo)
        policies = self._policies_factory.create_policies()
        rules_vo = vo.Rules(rules)

        return Project(
            project_id=project_value_objects.project_id,
            repo_id=project_value_objects.repository_id,
            provider=project_value_objects.provider,
            policies=policies,
            rules=rules_vo,
            url=url_vo,
            owner=project_value_objects.owner,
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now(),
        )
