from abc import ABC

from .specification import Specification


class ProjectAlreadyExistsSpecification[TQueryResult](Specification[TQueryResult], ABC):
    repo_id: str
