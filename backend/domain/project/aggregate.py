from datetime import datetime

from domain.entity import Entity
from domain.project import value_objects as vo


class Project(Entity):
    _id: vo.ProjectId
    _repo_id: vo.RepositoryId
    _provider: vo.Provider
    _policies: vo.Policies
    _owner: vo.Owner
    _rules: vo.Rules
    _url: vo.URL
    _created_at: datetime
    _updated_at: datetime

    def __init__(
        self,
        project_id: vo.ProjectId,
        repo_id: vo.RepositoryId,
        provider: vo.Provider,
        policies: vo.Policies,
        rules: vo.Rules,
        url: vo.URL,
        owner: vo.Owner,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self._id = project_id
        self._repo_id = repo_id
        self._provider = provider
        self._policies = policies
        self._rules = rules
        self._url = url
        self._owner = owner
        self._created_at = created_at
        self._updated_at = updated_at

    def id(self) -> str:
        """Return the id of the project."""
        return str(self._id)
