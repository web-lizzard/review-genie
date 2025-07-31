"""Project domain to ORM mapper functions."""

from adapters.outbound.persistence.sqlalchemy.models import ProjectModel
from domain.project.aggregate import Project


def from_domain(project: Project) -> ProjectModel:
    """Map domain Project aggregate to ORM ProjectModel.

    Args:
        project: Domain Project aggregate

    Returns:
        ProjectModel ORM instance
    """
    return ProjectModel(
        _project_id_value=str(project._id),
        _repo_id_value=str(project._repo_id),
        _provider_value=str(project._provider),
        _pull_request_policy=project._policies.pull_request_policy.value,
        _retry_limit_type=project._policies.retry_limit_type.value,
        _retry_limit_value=project._policies.retry_limit_value,
        _owner_value=str(project._owner),
        _url_value=str(project._url),
        _rules_text=project._rules.to_text(),
        created_at=project._created_at,
        updated_at=project._updated_at,
    )


def to_domain(model: ProjectModel) -> Project:
    """Map ORM ProjectModel to domain Project aggregate.

    Args:
        model: ProjectModel ORM instance

    Returns:
        Domain Project aggregate
    """
    return Project(
        project_id=model.project_id,
        repo_id=model.repo_id,
        provider=model.provider,
        policies=model.policies,
        rules=model.rules,
        url=model.url,
        owner=model.owner,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
