from pydantic import BaseModel


class Command(BaseModel):
    pass


class CreateProjectCommand(Command):
    rules: list[str]
    url: str
