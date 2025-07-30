from unittest.mock import AsyncMock

import pytest

from domain.project.aggregate import Project
from domain.project.exceptions import RemoteRepositoryDoesNotExistError
from domain.project.factories import DefaultPoliciesFactory, ProjectFactory, URLBasedValueObjectsFactory
from domain.project.ports import RemoteRepositoryVerifier
from domain.project.services.create_project_service import CreateProjectService
from domain.project.value_objects import ProviderType, Provider, RepositoryId


class TestCreateProjectService:
    """Test suite for CreateProjectService."""

    @pytest.fixture
    def policies_factory(self):
        """Create a policies factory for testing."""
        return DefaultPoliciesFactory()

    @pytest.fixture
    def value_objects_factory(self):
        """Create a value objects factory for testing."""
        return URLBasedValueObjectsFactory()

    @pytest.fixture
    def project_factory(self, policies_factory, value_objects_factory):
        """Create a project factory for testing."""
        return ProjectFactory(policies_factory, value_objects_factory)

    @pytest.fixture
    def mock_verifier_success(self):
        """Create a mock verifier that always returns True."""
        mock = AsyncMock(spec=RemoteRepositoryVerifier)
        mock.verify.return_value = True
        return mock

    @pytest.fixture
    def mock_verifier_failure(self):
        """Create a mock verifier that always returns False."""
        mock = AsyncMock(spec=RemoteRepositoryVerifier)
        mock.verify.return_value = False
        return mock

    @pytest.fixture
    def valid_project_data(self):
        """Provide valid data for creating a project that passes value object validation."""
        return {
            "url": "https://github.com/test-owner/test-repo",
            "rules": ["Code must be reviewed", "Tests must pass"],
        }

    @pytest.fixture
    def service_with_success_verifier(self, project_factory, value_objects_factory, mock_verifier_success):
        """Create service with a verifier that succeeds."""
        return CreateProjectService(
            project_factory=project_factory,
            value_objects_factory=value_objects_factory,
            remote_repository_verifiers=[mock_verifier_success],
        )

    @pytest.fixture
    def service_with_failure_verifier(self, project_factory, value_objects_factory, mock_verifier_failure):
        """Create service with a verifier that fails."""
        return CreateProjectService(
            project_factory=project_factory,
            value_objects_factory=value_objects_factory,
            remote_repository_verifiers=[mock_verifier_failure],
        )

    @pytest.fixture
    def service_with_multiple_verifiers(self, project_factory, value_objects_factory):
        """Create service with multiple verifiers for testing different scenarios."""
        success_verifier = AsyncMock(spec=RemoteRepositoryVerifier)
        success_verifier.verify.return_value = True

        failure_verifier = AsyncMock(spec=RemoteRepositoryVerifier)
        failure_verifier.verify.return_value = False

        return (
            CreateProjectService(
                project_factory=project_factory,
                value_objects_factory=value_objects_factory,
                remote_repository_verifiers=[success_verifier, failure_verifier],
            ),
            success_verifier,
            failure_verifier,
        )

    @pytest.mark.asyncio
    async def test_create_project_success(
        self, service_with_success_verifier, valid_project_data, mock_verifier_success
    ):
        """Test successful project creation when verifier returns True."""
        # Act
        result = await service_with_success_verifier.create(**valid_project_data)

        # Assert
        assert isinstance(result, Project)
        assert str(result._repo_id) == "test-repo"
        assert str(result._provider) == ProviderType.GITHUB.value
        assert str(result._owner) == "test-owner"
        assert result._rules.rules == valid_project_data["rules"]
        assert str(result._url) == valid_project_data["url"]

        # Verify verifier was called with correct parameters extracted from URL
        mock_verifier_success.verify.assert_called_once_with(
            repository_id=RepositoryId("test-repo"), provider=Provider(ProviderType.GITHUB)
        )

    @pytest.mark.asyncio
    async def test_create_project_failure_verification(
        self, service_with_failure_verifier, valid_project_data, mock_verifier_failure
    ):
        """Test that RemoteRepositoryDoesNotExistError is raised when verifier returns False."""
        # Act & Assert
        with pytest.raises(RemoteRepositoryDoesNotExistError) as exc_info:
            await service_with_failure_verifier.create(**valid_project_data)

        # Verify exception message contains the expected information
        expected_message = f"Remote repository 'test-repo' does not exist on provider 'github'"
        assert str(exc_info.value) == expected_message

        # Verify verifier was called with correct parameters extracted from URL
        mock_verifier_failure.verify.assert_called_once_with(
            repository_id=RepositoryId("test-repo"), provider=Provider(ProviderType.GITHUB)
        )

    @pytest.mark.asyncio
    async def test_create_project_multiple_verifiers_all_succeed(
        self, service_with_multiple_verifiers, valid_project_data
    ):
        """Test project creation when first verifier succeeds (loop breaks, second not called)."""
        service, success_verifier, failure_verifier = service_with_multiple_verifiers

        # Configure first verifier to succeed
        success_verifier.verify.return_value = True
        failure_verifier.verify.return_value = (
            True  # This won't matter since first succeeds
        )

        # Act
        result = await service.create(**valid_project_data)

        # Assert
        assert isinstance(result, Project)

        # Verify only first verifier was called (loop breaks on first success)
        success_verifier.verify.assert_called_once_with(
            repository_id=RepositoryId("test-repo"), provider=Provider(ProviderType.GITHUB)
        )
        # Second verifier should NOT be called because loop breaks on first success
        failure_verifier.verify.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_project_multiple_verifiers_first_fails_second_succeeds(
        self, service_with_multiple_verifiers, valid_project_data
    ):
        """Test that verification succeeds when first verifier fails but second succeeds."""
        service, success_verifier, failure_verifier = service_with_multiple_verifiers

        # Configure first verifier to fail, second to succeed
        success_verifier.verify.return_value = False
        failure_verifier.verify.return_value = True

        # Act
        result = await service.create(**valid_project_data)

        # Assert
        assert isinstance(result, Project)

        # Verify both verifiers were called
        success_verifier.verify.assert_called_once_with(
            repository_id=RepositoryId("test-repo"), provider=Provider(ProviderType.GITHUB)
        )
        failure_verifier.verify.assert_called_once_with(
            repository_id=RepositoryId("test-repo"), provider=Provider(ProviderType.GITHUB)
        )

    @pytest.mark.asyncio
    async def test_create_project_multiple_verifiers_all_fail(
        self, service_with_multiple_verifiers, valid_project_data
    ):
        """Test that verification fails when all verifiers fail."""
        service, success_verifier, failure_verifier = service_with_multiple_verifiers

        # Configure both to fail
        success_verifier.verify.return_value = False
        failure_verifier.verify.return_value = False

        # Act & Assert
        with pytest.raises(RemoteRepositoryDoesNotExistError):
            await service.create(**valid_project_data)

        # Verify both verifiers were called
        success_verifier.verify.assert_called_once_with(
            repository_id=RepositoryId("test-repo"), provider=Provider(ProviderType.GITHUB)
        )
        failure_verifier.verify.assert_called_once_with(
            repository_id=RepositoryId("test-repo"), provider=Provider(ProviderType.GITHUB)
        )

    @pytest.mark.asyncio
    async def test_create_project_with_different_providers(
        self, service_with_success_verifier, mock_verifier_success
    ):
        """Test project creation with different valid providers."""
        test_cases = [
            {
                "url": "https://github.com/test-owner/test-repo",
                "expected_provider": ProviderType.GITHUB,
                "expected_repo": "test-repo",
                "expected_owner": "test-owner",
            },
            {
                "url": "https://gitlab.com/test-owner/test-repo",
                "expected_provider": ProviderType.GITLAB,
                "expected_repo": "test-repo",
                "expected_owner": "test-owner",
            },
            {
                "url": "https://bitbucket.org/test-owner/test-repo",
                "expected_provider": ProviderType.BITBUCKET,
                "expected_repo": "test-repo",
                "expected_owner": "test-owner",
            },
        ]

        for case in test_cases:
            mock_verifier_success.reset_mock()

            data = {"url": case["url"], "rules": ["Standard rules"]}
            result = await service_with_success_verifier.create(**data)

            assert isinstance(result, Project)
            assert str(result._provider) == case["expected_provider"].value
            assert str(result._repo_id) == case["expected_repo"]
            assert str(result._owner) == case["expected_owner"]
            mock_verifier_success.verify.assert_called_once_with(
                repository_id=RepositoryId(case["expected_repo"]),
                provider=Provider(case["expected_provider"])
            )

    @pytest.mark.asyncio
    async def test_create_project_with_empty_rules(
        self, service_with_success_verifier, valid_project_data
    ):
        """Test project creation with empty rules list stays empty."""
        # Arrange
        data = {**valid_project_data, "rules": []}

        # Act
        result = await service_with_success_verifier.create(**data)

        # Assert
        assert isinstance(result, Project)
        # Empty rules should remain empty
        assert len(result._rules.rules) == 0
        assert result._rules.rules == []

    @pytest.mark.asyncio
    async def test_create_project_with_custom_rules(
        self, service_with_success_verifier, valid_project_data
    ):
        """Test project creation with custom rules."""
        # Arrange
        custom_rules = [
            "Custom rule 1",
            "Custom rule 2",
            "Must follow specific coding standards",
        ]
        data = {**valid_project_data, "rules": custom_rules}

        # Act
        result = await service_with_success_verifier.create(**data)

        # Assert
        assert isinstance(result, Project)
        assert result._rules.rules == custom_rules

    @pytest.mark.asyncio
    async def test_create_project_with_edge_case_valid_urls(
        self, service_with_success_verifier
    ):
        """Test project creation with edge cases for valid URLs."""
        edge_cases = [
            {
                "url": "https://github.com/a/a",
                "expected_repo": "a",
                "expected_owner": "a",
            },
            {
                "url": "https://gitlab.com/owner-with-hyphens/repo-with-hyphens",
                "expected_repo": "repo-with-hyphens",
                "expected_owner": "owner-with-hyphens",
            },
            {
                "url": "https://bitbucket.org/owner123/repo.with.dots",
                "expected_repo": "repo.with.dots",
                "expected_owner": "owner123",
            },
        ]

        for case in edge_cases:
            data = {"url": case["url"], "rules": ["Rule 1"]}
            result = await service_with_success_verifier.create(**data)
            assert isinstance(result, Project)
            assert str(result._repo_id) == case["expected_repo"]
            assert str(result._owner) == case["expected_owner"]
