from abc import ABC

from domain.ports import Specification


class ProjectAlreadyExistsSpecification[TQueryResult](Specification[TQueryResult], ABC):
    repo_id: str
