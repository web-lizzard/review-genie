from typing import Protocol

from domain.project import value_objects as vo


class RemoteRepositoryVerifier(Protocol):
    async def verify(
        self, repository_id: vo.RepositoryId, provider: vo.Provider
    ) -> bool: ...
