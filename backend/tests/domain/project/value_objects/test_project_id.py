import pytest

from domain.project.exceptions import InvalidProjectIdentifierFormatError
from domain.project.value_objects import ProjectId, ProviderType


class TestProjectId:
    """Test cases for ProjectId value object."""

    @pytest.mark.parametrize(
        "valid_project_id",
        [
            "github:user:repo",
            "gitlab:organization:my-repo",
            "bitbucket:user123:repo-123",
            "github:org-name:repo.name",
            "gitlab:MyOrg:repo_name",
            "bitbucket:a:a",
            "github:test-user:complex-repo_name.git",
            "gitlab:123:project.test",
        ],
    )
    def test_valid_project_id_creation(self, valid_project_id: str) -> None:
        """Test creating ProjectId with valid format provider:owner:repo_id."""
        project_id = ProjectId(valid_project_id)
        assert project_id.value == valid_project_id
        assert project_id.id == valid_project_id
        assert str(project_id) == valid_project_id

    @pytest.mark.parametrize(
        "provider, owner, repo_id",
        [
            ("github", "user", "repo"),
            ("gitlab", "organization", "my-repo"),
            ("bitbucket", "user123", "repo-123"),
            ("github", "org-name", "repo.name"),
            ("gitlab", "MyOrg", "repo_name"),
        ],
    )
    def test_valid_project_id_components(
        self, provider: str, owner: str, repo_id: str
    ) -> None:
        """Test ProjectId creation with valid individual components."""
        project_id_value = f"{provider}:{owner}:{repo_id}"
        project_id = ProjectId(project_id_value)
        assert project_id.value == project_id_value

    @pytest.mark.parametrize(
        "invalid_project_id",
        [
            # Wrong number of parts
            "github:user",  # Missing repo_id
            "github",  # Only provider
            "",  # Empty string
            "github:user:repo:extra",  # Too many parts
            ":user:repo",  # Empty provider
            "github::repo",  # Empty owner
            "github:user:",  # Empty repo_id
            # Invalid provider
            "unknown:user:repo",  # Unsupported provider
            "svn:user:repo",  # Another unsupported provider
            "git:user:repo",  # Yet another unsupported provider
            # Invalid owner format
            "github:-user:repo",  # Owner starts with hyphen
            "github:user-:repo",  # Owner ends with hyphen
            "github:user@name:repo",  # Invalid character in owner
            "github:user.name:repo",  # Dot in owner
            "github:user_name:repo",  # Underscore in owner
            "github:user name:repo",  # Space in owner
            "github::repo",  # Empty owner
            # Invalid repo_id format
            "github:user:-repo",  # Repo starts with hyphen
            "github:user:repo-",  # Repo ends with hyphen
            "github:user:.repo",  # Repo starts with dot
            "github:user:repo.",  # Repo ends with dot
            "github:user:_repo",  # Repo starts with underscore
            "github:user:repo_",  # Repo ends with underscore
            "github:user:repo@name",  # Invalid character in repo
            "github:user:repo name",  # Space in repo
            "github:user:",  # Empty repo_id
        ],
    )
    def test_invalid_project_id_creation(self, invalid_project_id: str) -> None:
        """Test that ProjectId raises InvalidProjectIdentifierFormatError for invalid formats."""
        with pytest.raises(InvalidProjectIdentifierFormatError):
            ProjectId(invalid_project_id)

    def test_project_id_immutability(self) -> None:
        """Test that ProjectId is immutable (frozen dataclass)."""
        project_id = ProjectId("github:user:repo")
        with pytest.raises(AttributeError):
            project_id.value = "gitlab:user:repo"  # type: ignore

    def test_project_id_equality(self) -> None:
        """Test ProjectId equality comparison."""
        project_id1 = ProjectId("github:user:repo")
        project_id2 = ProjectId("github:user:repo")
        project_id3 = ProjectId("gitlab:user:repo")

        assert project_id1 == project_id2
        assert project_id1 != project_id3
        assert hash(project_id1) == hash(project_id2)
        assert hash(project_id1) != hash(project_id3)

    def test_project_id_properties(self) -> None:
        """Test ProjectId id property."""
        project_id_value = "github:user:repo"
        project_id = ProjectId(project_id_value)

        assert project_id.id == project_id_value
        assert project_id.value == project_id_value

    def test_project_id_str_representation(self) -> None:
        """Test string representation of ProjectId."""
        project_id_value = "github:user:repo"
        project_id = ProjectId(project_id_value)
        assert str(project_id) == project_id_value

    @pytest.mark.parametrize(
        "provider_type",
        [
            ProviderType.GITHUB,
            ProviderType.GITLAB,
            ProviderType.BITBUCKET,
        ],
    )
    def test_project_id_with_all_providers(self, provider_type: ProviderType) -> None:
        """Test ProjectId creation with all supported providers."""
        project_id_value = f"{provider_type.value}:user:repo"
        project_id = ProjectId(project_id_value)
        assert project_id.value == project_id_value

    def test_project_id_edge_cases(self) -> None:
        """Test edge cases for ProjectId validation."""
        # Minimum valid format
        minimal = ProjectId("github:a:a")
        assert minimal.value == "github:a:a"

        # Complex valid format
        complex_id = ProjectId("gitlab:complex-org123:repo-name_with.dots123")
        assert complex_id.value == "gitlab:complex-org123:repo-name_with.dots123"

    def test_project_id_case_sensitivity(self) -> None:
        """Test that ProjectId maintains case sensitivity."""
        mixed_case = ProjectId("github:MyOrg:MyRepo")
        assert mixed_case.value == "github:MyOrg:MyRepo"

        # Should be different from lowercase version
        lowercase = ProjectId("github:myorg:myrepo")
        assert mixed_case != lowercase

    def test_project_id_format_validation_details(self) -> None:
        """Test specific format validation rules."""
        # Valid owner patterns
        valid_owners = ["user", "org-123", "MyOrg", "123", "a"]
        for owner in valid_owners:
            project_id = ProjectId(f"github:{owner}:repo")
            assert project_id.value == f"github:{owner}:repo"

        # Valid repo patterns
        valid_repos = [
            "repo",
            "my-repo",
            "repo.git",
            "repo_name",
            "repo-name_with.dots",
            "123",
            "a",
        ]
        for repo in valid_repos:
            project_id = ProjectId(f"github:user:{repo}")
            assert project_id.value == f"github:user:{repo}"
