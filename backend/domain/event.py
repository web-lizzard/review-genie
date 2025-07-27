import datetime
import uuid

from pydantic import BaseModel, Field


class DomainEvent(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    occurred_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )

    class Config:
        frozen = True

    def serialize(self) -> dict:
        return self.model_dump()

    @property
    def type(self) -> str:
        return self.__class__.__name__

    @classmethod
    def deserialize(cls, data: dict) -> "DomainEvent":
        return cls(**data)
