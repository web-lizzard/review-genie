from abc import ABC, abstractmethod

from pydantic import BaseModel


class Specification[TQuery](BaseModel, ABC):
    pass

    @abstractmethod
    def to_query(self) -> TQuery:
        """Convert the specification to a query."""
        raise NotImplementedError
