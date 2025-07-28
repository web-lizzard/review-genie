from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from pydantic import BaseModel

from domain.entity import Entity


class Specification[TQuery](BaseModel):
    pass

    @abstractmethod
    def to_query(self) -> TQuery:
        """Convert the specification to a query."""
        raise NotImplementedError


class ReadRepository[TQueryResult](ABC):
    @abstractmethod
    async def find_one(self, specification: Specification) -> TQueryResult:
        """Find a repository by id. Raise EntityNotFoundError if not found."""
        raise NotImplementedError

    @abstractmethod
    async def find_all(self, specification: Specification) -> list[TQueryResult]:
        """Find all repositories."""
        raise NotImplementedError


class SaveRepository[TEntity: Entity](ABC):
    @abstractmethod
    async def save(self, entity: TEntity) -> None:
        """Save a repository to the database."""
        raise NotImplementedError


class UnitOfWork[TQueryResult](ABC):
    async def __aenter__(self) -> Self:
        """Enter the context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the context manager."""
        await self.rollback()

    @abstractmethod
    async def commit(self) -> None:
        """Commit the current transaction."""
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the current transaction."""
        raise NotImplementedError

    @abstractmethod
    async def save(self, entity: Entity) -> None:
        """Save an entity to the database."""
        raise NotImplementedError

    @abstractmethod
    async def make_query(self, specification: Specification) -> TQueryResult:
        """Make a query to the database."""
        raise NotImplementedError
