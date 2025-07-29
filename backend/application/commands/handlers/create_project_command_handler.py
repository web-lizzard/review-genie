from collections.abc import Callable

from application.commands.commands import CreateProjectCommand
from domain.ports import UnitOfWork
from domain.project.exceptions import ProjectAlreadyExistsError
from domain.project.services import CreateProjectService
from domain.specifications import ProjectAlreadyExistsSpecification


class CreateProjectCommandHandler:
    def __init__(
        self,
        uow: UnitOfWork[bool],
        create_project_service: CreateProjectService,
        specification_factory: Callable[
            [CreateProjectCommand], ProjectAlreadyExistsSpecification
        ],
    ):
        self._uow = uow
        self._create_project_service = create_project_service
        self._specification_factory = specification_factory

    async def handle(self, command: CreateProjectCommand) -> None:
        async with self._uow as uow:
            spec = self._specification_factory(command)
            is_project_already_exists = await uow.make_query(spec)
            if is_project_already_exists:
                raise ProjectAlreadyExistsError(command.repo_id)

            project = await self._create_project_service.create(
                command.repo_id,
                command.provider,
                command.owner,
                command.rules,
                command.url,
            )
            await uow.save(project)
            await uow.commit()
