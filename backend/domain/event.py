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
