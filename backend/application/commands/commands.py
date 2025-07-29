from pydantic import BaseModel


class Command(BaseModel):
    pass


class CreateProjectCommand(Command):
    repo_id: str
    provider: str
    owner: str
    rules: list[str]
    url: str
