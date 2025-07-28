from typing import Protocol


class RemoteRepositoryVerifier(Protocol):
    async def verify(self, repository_id: str, provider: str) -> bool: ...
