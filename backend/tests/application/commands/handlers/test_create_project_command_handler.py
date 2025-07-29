from unittest.mock import AsyncMock, Mock

import pytest

from application.commands.commands import CreateProjectCommand
from application.commands.handlers.create_project_command_handler import (
    CreateProjectCommandHandler,
)
from domain.project.aggregate import Project
from domain.project.exceptions import ProjectAlreadyExistsError
from domain.project.services.create_project_service import CreateProjectService
from domain.ports import UnitOfWork
from domain.ports.specifications import ProjectAlreadyExistsSpecification


class TestCreateProjectCommandHandler:
    """Test suite for CreateProjectCommandHandler focusing on application layer responsibilities."""

    @pytest.fixture
    def mock_uow(self):
        """Create a mock Unit of Work."""
        mock = AsyncMock(spec=UnitOfWork)
        # Configure the context manager
        mock.__aenter__.return_value = mock
        mock.__aexit__.return_value = None
        return mock

    @pytest.fixture
    def mock_create_project_service(self):
        """Create a mock CreateProjectService."""
        return AsyncMock(spec=CreateProjectService)

    @pytest.fixture
    def mock_specification_factory(self):
        """Create a mock specification factory."""
        mock_spec = Mock(spec=ProjectAlreadyExistsSpecification)
        return Mock(return_value=mock_spec)

    @pytest.fixture
    def mock_project(self):
        """Create a mock Project for testing."""
        return Mock(spec=Project)

    @pytest.fixture
    def valid_command(self):
        """Create a valid CreateProjectCommand for testing."""
        return CreateProjectCommand(
            repo_id="test-repo",
            provider="github",
            owner="test-owner",
            rules=["Rule 1", "Rule 2"],
            url="https://github.com/test-owner/test-repo",
        )

    @pytest.fixture
    def handler(self, mock_uow, mock_create_project_service, mock_specification_factory):
        """Create a CreateProjectCommandHandler with mocked dependencies."""
        return CreateProjectCommandHandler(
            uow=mock_uow,
            create_project_service=mock_create_project_service,
            specification_factory=mock_specification_factory,
        )

    @pytest.mark.asyncio
    async def test_handle_successful_project_creation(
        self,
        handler,
        valid_command,
        mock_uow,
        mock_create_project_service,
        mock_specification_factory,
        mock_project,
    ):
        """Test successful project creation when project doesn't already exist."""
        # Arrange
        mock_uow.make_query.return_value = False  # Project doesn't exist
        mock_create_project_service.create.return_value = mock_project
        expected_spec = mock_specification_factory.return_value

        # Act
        await handler.handle(valid_command)

        # Assert - Application layer responsibilities
        # 1. Transaction management
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

        # 2. Specification factory usage
        mock_specification_factory.assert_called_once_with(valid_command)

        # 3. Query execution
        mock_uow.make_query.assert_called_once_with(expected_spec)

        # 4. Domain service orchestration
        mock_create_project_service.create.assert_called_once_with(
            valid_command.repo_id,
            valid_command.provider,
            valid_command.owner,
            valid_command.rules,
            valid_command.url,
        )

        # 5. Entity persistence
        mock_uow.save.assert_called_once_with(mock_project)

        # 6. Transaction commit
        mock_uow.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_project_already_exists(
        self,
        handler,
        valid_command,
        mock_uow,
        mock_create_project_service,
        mock_specification_factory,
    ):
        """Test that ProjectAlreadyExistsError is raised when project already exists."""
        # Arrange
        mock_uow.make_query.return_value = True  # Project already exists
        expected_spec = mock_specification_factory.return_value

        # Act & Assert
        with pytest.raises(ProjectAlreadyExistsError) as exc_info:
            await handler.handle(valid_command)

        # Verify exception contains expected repo_id
        assert str(exc_info.value).find(valid_command.repo_id) != -1

        # Assert - Application layer responsibilities
        # 1. Specification factory was called
        mock_specification_factory.assert_called_once_with(valid_command)

        # 2. Query was executed
        mock_uow.make_query.assert_called_once_with(expected_spec)

        # 3. Domain service should NOT be called when project exists
        mock_create_project_service.create.assert_not_called()

        # 4. No save or commit should happen
        mock_uow.save.assert_not_called()
        mock_uow.commit.assert_not_called()

        # 5. Transaction context is still managed
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_domain_service_exception_propagates(
        self,
        handler,
        valid_command,
        mock_uow,
        mock_create_project_service,
        mock_specification_factory,
    ):
        """Test that exceptions from domain service are propagated correctly."""
        # Arrange
        mock_uow.make_query.return_value = False  # Project doesn't exist
        domain_exception = Exception("Domain service error")
        mock_create_project_service.create.side_effect = domain_exception

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await handler.handle(valid_command)

        assert exc_info.value is domain_exception

        # Assert - Application layer behavior under exception
        # 1. Domain service was called
        mock_create_project_service.create.assert_called_once()

        # 2. Save and commit should NOT be called when exception occurs
        mock_uow.save.assert_not_called()
        mock_uow.commit.assert_not_called()

        # 3. Transaction context is managed (rollback via __aexit__)
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_query_exception_propagates(
        self,
        handler,
        valid_command,
        mock_uow,
        mock_create_project_service,
        mock_specification_factory,
    ):
        """Test that exceptions from UoW query are propagated correctly."""
        # Arrange
        query_exception = Exception("Query execution error")
        mock_uow.make_query.side_effect = query_exception

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await handler.handle(valid_command)

        assert exc_info.value is query_exception

        # Assert - Application layer behavior under exception
        # 1. Specification factory was called
        mock_specification_factory.assert_called_once_with(valid_command)

        # 2. Domain service should NOT be called when query fails
        mock_create_project_service.create.assert_not_called()

        # 3. No save or commit should happen
        mock_uow.save.assert_not_called()
        mock_uow.commit.assert_not_called()

        # 4. Transaction context is managed
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_save_exception_propagates(
        self,
        handler,
        valid_command,
        mock_uow,
        mock_create_project_service,
        mock_specification_factory,
        mock_project,
    ):
        """Test that exceptions from UoW save are propagated correctly."""
        # Arrange
        mock_uow.make_query.return_value = False
        mock_create_project_service.create.return_value = mock_project
        save_exception = Exception("Save operation error")
        mock_uow.save.side_effect = save_exception

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await handler.handle(valid_command)

        assert exc_info.value is save_exception

        # Assert - Application layer behavior under exception
        # 1. Domain service was called
        mock_create_project_service.create.assert_called_once()

        # 2. Save was attempted
        mock_uow.save.assert_called_once_with(mock_project)

        # 3. Commit should NOT be called when save fails
        mock_uow.commit.assert_not_called()

        # 4. Transaction context is managed
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_commit_exception_propagates(
        self,
        handler,
        valid_command,
        mock_uow,
        mock_create_project_service,
        mock_specification_factory,
        mock_project,
    ):
        """Test that exceptions from UoW commit are propagated correctly."""
        # Arrange
        mock_uow.make_query.return_value = False
        mock_create_project_service.create.return_value = mock_project
        commit_exception = Exception("Commit operation error")
        mock_uow.commit.side_effect = commit_exception

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await handler.handle(valid_command)

        assert exc_info.value is commit_exception

        # Assert - Application layer behavior under exception
        # 1. All operations up to commit were called
        mock_create_project_service.create.assert_called_once()
        mock_uow.save.assert_called_once_with(mock_project)
        mock_uow.commit.assert_called_once()

        # 2. Transaction context is managed
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_with_different_command_parameters(
        self,
        mock_uow,
        mock_create_project_service,
        mock_specification_factory,
        mock_project,
    ):
        """Test handler works correctly with different command parameters."""
        # Arrange
        handler = CreateProjectCommandHandler(
            uow=mock_uow,
            create_project_service=mock_create_project_service,
            specification_factory=mock_specification_factory,
        )

        command = CreateProjectCommand(
            repo_id="different-repo",
            provider="gitlab",
            owner="different-owner",
            rules=[],  # Empty rules
            url="https://gitlab.com/different-owner/different-repo",
        )

        mock_uow.make_query.return_value = False
        mock_create_project_service.create.return_value = mock_project

        # Act
        await handler.handle(command)

        # Assert - Verify correct parameters passed to domain service
        mock_create_project_service.create.assert_called_once_with(
            "different-repo",
            "gitlab",
            "different-owner",
            [],
            "https://gitlab.com/different-owner/different-repo",
        )

        # Assert - Verify specification factory called with correct command
        mock_specification_factory.assert_called_once_with(command)

    @pytest.mark.asyncio
    async def test_handle_preserves_command_data_integrity(
        self,
        handler,
        mock_uow,
        mock_create_project_service,
        mock_specification_factory,
        mock_project,
    ):
        """Test that command data is passed correctly without modification."""
        # Arrange
        command = CreateProjectCommand(
            repo_id="test-repo-123",
            provider="bitbucket",
            owner="test-owner-456",
            rules=["Rule A", "Rule B", "Rule C"],
            url="https://bitbucket.org/test-owner-456/test-repo-123",
        )

        mock_uow.make_query.return_value = False
        mock_create_project_service.create.return_value = mock_project

        # Act
        await handler.handle(command)

        # Assert - Verify exact parameter passing
        mock_create_project_service.create.assert_called_once_with(
            command.repo_id,
            command.provider,
            command.owner,
            command.rules,
            command.url,
        )

        # Verify specification factory gets the original command
        mock_specification_factory.assert_called_once_with(command)
